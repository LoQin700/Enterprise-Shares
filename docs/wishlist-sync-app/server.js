import crypto from 'node:crypto';
import express from 'express';

const app = express();
app.use(express.json({ limit: '64kb' }));

const {
  PORT = '3000',
  SHOPIFY_SHOP,
  SHOPIFY_API_SECRET,
  SHOPIFY_ADMIN_ACCESS_TOKEN,
  SHOPIFY_API_VERSION = '2026-07',
  WISHLIST_NAMESPACE = 'enterprise_shares',
  WISHLIST_KEY = 'wishlist'
} = process.env;

const required = {
  SHOPIFY_SHOP,
  SHOPIFY_API_SECRET,
  SHOPIFY_ADMIN_ACCESS_TOKEN
};

for (const [key, value] of Object.entries(required)) {
  if (!value) throw new Error(`Missing required environment variable: ${key}`);
}

const secureCompare = (left, right) => {
  const a = Buffer.from(left || '', 'utf8');
  const b = Buffer.from(right || '', 'utf8');
  return a.length === b.length && crypto.timingSafeEqual(a, b);
};

const verifyAppProxy = (request) => {
  const url = new URL(`${request.protocol}://${request.get('host')}${request.originalUrl}`);
  const suppliedSignature = url.searchParams.get('signature') || '';
  const grouped = new Map();

  for (const [key, value] of url.searchParams.entries()) {
    if (key === 'signature') continue;
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(value);
  }

  const message = [...grouped.entries()]
    .map(([key, values]) => `${key}=${values.join(',')}`)
    .sort()
    .join('');

  const calculated = crypto
    .createHmac('sha256', SHOPIFY_API_SECRET)
    .update(message)
    .digest('hex');

  if (!secureCompare(suppliedSignature, calculated)) {
    const error = new Error('Invalid app proxy signature');
    error.status = 401;
    throw error;
  }

  const shop = url.searchParams.get('shop');
  if (shop !== SHOPIFY_SHOP) {
    const error = new Error('Unexpected shop');
    error.status = 403;
    throw error;
  }

  const timestamp = Number(url.searchParams.get('timestamp'));
  if (!Number.isFinite(timestamp) || Math.abs(Date.now() / 1000 - timestamp) > 300) {
    const error = new Error('Expired app proxy request');
    error.status = 401;
    throw error;
  }

  const customerId = url.searchParams.get('logged_in_customer_id');
  if (!customerId || !/^\d+$/.test(customerId)) {
    const error = new Error('Customer login required');
    error.status = 401;
    throw error;
  }

  return customerId;
};

const normalizeHandles = (items) => {
  if (!Array.isArray(items)) return [];
  return [...new Set(items
    .filter((item) => typeof item === 'string' && /^[a-z0-9][a-z0-9-]*$/.test(item))
    .slice(0, 200))];
};

const adminGraphql = async (query, variables) => {
  const response = await fetch(`https://${SHOPIFY_SHOP}/admin/api/${SHOPIFY_API_VERSION}/graphql.json`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Access-Token': SHOPIFY_ADMIN_ACCESS_TOKEN
    },
    body: JSON.stringify({ query, variables })
  });

  const payload = await response.json();
  if (!response.ok || payload.errors) {
    throw new Error(`Shopify Admin API error: ${JSON.stringify(payload.errors || payload)}`);
  }
  return payload.data;
};

const readWishlist = async (customerId) => {
  const data = await adminGraphql(`
    query CustomerWishlist($id: ID!, $namespace: String!, $key: String!) {
      customer(id: $id) {
        metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }
  `, {
    id: `gid://shopify/Customer/${customerId}`,
    namespace: WISHLIST_NAMESPACE,
    key: WISHLIST_KEY
  });

  const raw = data.customer?.metafield?.value;
  if (!raw) return [];

  try {
    return normalizeHandles(JSON.parse(raw));
  } catch (_) {
    return [];
  }
};

const writeWishlist = async (customerId, items) => {
  const normalized = normalizeHandles(items);
  const data = await adminGraphql(`
    mutation SetCustomerWishlist($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields { id value }
        userErrors { field message code }
      }
    }
  `, {
    metafields: [{
      ownerId: `gid://shopify/Customer/${customerId}`,
      namespace: WISHLIST_NAMESPACE,
      key: WISHLIST_KEY,
      type: 'json',
      value: JSON.stringify(normalized)
    }]
  });

  const errors = data.metafieldsSet?.userErrors || [];
  if (errors.length) throw new Error(`Metafield write failed: ${JSON.stringify(errors)}`);
  return normalized;
};

app.get('/health', (_request, response) => {
  response.json({ ok: true });
});

app.get('/proxy/wishlist', async (request, response, next) => {
  try {
    const customerId = verifyAppProxy(request);
    const items = await readWishlist(customerId);
    response.set('Cache-Control', 'no-store');
    response.json({ items });
  } catch (error) {
    next(error);
  }
});

app.post('/proxy/wishlist', async (request, response, next) => {
  try {
    const customerId = verifyAppProxy(request);
    const items = await writeWishlist(customerId, request.body?.items);
    response.set('Cache-Control', 'no-store');
    response.json({ items });
  } catch (error) {
    next(error);
  }
});

app.use((error, _request, response, _next) => {
  console.error(error);
  response.status(error.status || 500).json({ error: error.message || 'Unexpected error' });
});

app.listen(Number(PORT), () => {
  console.log(`Enterprise Shares wishlist sync listening on port ${PORT}`);
});
