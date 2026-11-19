'use strict';
// Runs one browser script against stubbed document, location and fetch,
// and prints what it did as JSON. Input arrives on stdin.
const fs = require('fs');
const vm = require('vm');

const sc = JSON.parse(fs.readFileSync(0, 'utf8'));
const out = { options: [], value: null, navigated: [], fetched: [], errors: [] };

process.on('unhandledRejection', (e) => out.errors.push('unhandledRejection: ' + e));
process.on('uncaughtException', (e) => out.errors.push('uncaughtException: ' + e));

function El(tag) {
  this.tag = tag;
  this.children = [];
  this.listeners = {};
  this.value = '';
  this.textContent = '';
}
El.prototype.appendChild = function (c) { this.children.push(c); return c; };
El.prototype.addEventListener = function (type, fn) { this.listeners[type] = fn; };
Object.defineProperty(El.prototype, 'innerHTML', {
  set: function () { this.children = []; },
  get: function () { return ''; },
});

const select = new El('select');
const document = {
  querySelector: function (q) {
    if (q.indexOf('blis-design-version') >= 0) {
      return sc.meta === null || sc.meta === undefined ? null : { content: sc.meta };
    }
    return null;
  },
  getElementById: function (id) { return id === 'blis-version' ? select : null; },
  createElement: function (tag) { return new El(tag); },
};

const href = sc.href || 'https://example.github.io/blis-design/v1.0.0/blis-target-design.html';
const location = {
  href: href,
  pathname: sc.pathname || new URL(href).pathname,
  hash: sc.hash || '',
  assign: function (u) { out.navigated.push(u); },
  replace: function (u) { out.navigated.push(u); },
};

const mode = sc.fetch || 'absent';
function stubFetch(url) {
  out.fetched.push(String(url));
  if (mode === 'throw') throw new TypeError('fetch is not allowed here');
  if (mode === 'reject') return Promise.reject(new TypeError('Failed to fetch'));
  if (mode === 'notok') return Promise.resolve({ ok: false, status: 404, json: () => Promise.resolve({}) });
  if (mode === 'badjson') return Promise.resolve({ ok: true, status: 200, json: () => Promise.reject(new SyntaxError('bad json')) });
  return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(sc.versions) });
}
const context = { document: document, location: location, console: console };
if (mode !== 'absent') context.fetch = stubFetch;
vm.createContext(context);

(async function () {
  try {
    vm.runInContext(sc.script, context);
  } catch (e) {
    out.errors.push('script threw: ' + e);
  }
  await new Promise((r) => setTimeout(r, 30));
  if (sc.choose) {
    select.value = sc.choose;
    try {
      if (select.listeners.change) select.listeners.change({ target: select });
    } catch (e) {
      out.errors.push('change handler threw: ' + e);
    }
    await new Promise((r) => setTimeout(r, 30));
  }
  out.options = select.children.map((o) => ({ value: o.value, text: o.textContent }));
  out.value = select.value;
  process.stdout.write(JSON.stringify(out));
})();
