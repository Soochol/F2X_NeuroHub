var __defProp = Object.defineProperty;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __publicField = (obj, key, value) => __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);
import { j as jsxRuntimeExports, Q as QueryClient, u as useQuery, a as useQueryClient, b as useMutation, c as QueryClientProvider } from "./query-B1euMQrZ.js";
import { b as requireReactDom, a as reactExports, u as useLocation, N as NavLink, c as commonjsGlobal, g as getDefaultExportFromCjs, R as React, d as useNavigate, e as useParams, f as Routes, h as Route, B as BrowserRouter } from "./vendor-CZPWNuc-.js";
import { c as create } from "./state-D0aMv-f7.js";
(function polyfill() {
  const relList = document.createElement("link").relList;
  if (relList && relList.supports && relList.supports("modulepreload")) {
    return;
  }
  for (const link of document.querySelectorAll('link[rel="modulepreload"]')) {
    processPreload(link);
  }
  new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type !== "childList") {
        continue;
      }
      for (const node of mutation.addedNodes) {
        if (node.tagName === "LINK" && node.rel === "modulepreload")
          processPreload(node);
      }
    }
  }).observe(document, { childList: true, subtree: true });
  function getFetchOpts(link) {
    const fetchOpts = {};
    if (link.integrity) fetchOpts.integrity = link.integrity;
    if (link.referrerPolicy) fetchOpts.referrerPolicy = link.referrerPolicy;
    if (link.crossOrigin === "use-credentials")
      fetchOpts.credentials = "include";
    else if (link.crossOrigin === "anonymous") fetchOpts.credentials = "omit";
    else fetchOpts.credentials = "same-origin";
    return fetchOpts;
  }
  function processPreload(link) {
    if (link.ep)
      return;
    link.ep = true;
    const fetchOpts = getFetchOpts(link);
    fetch(link.href, fetchOpts);
  }
})();
var client = {};
var hasRequiredClient;
function requireClient() {
  if (hasRequiredClient) return client;
  hasRequiredClient = 1;
  var m = requireReactDom();
  {
    client.createRoot = m.createRoot;
    client.hydrateRoot = m.hydrateRoot;
  }
  return client;
}
var clientExports = requireClient();
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const toKebabCase = (string) => string.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase();
const mergeClasses = (...classes) => classes.filter((className, index, array) => {
  return Boolean(className) && className.trim() !== "" && array.indexOf(className) === index;
}).join(" ").trim();
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
var defaultAttributes = {
  xmlns: "http://www.w3.org/2000/svg",
  width: 24,
  height: 24,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round"
};
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Icon = reactExports.forwardRef(
  ({
    color = "currentColor",
    size = 24,
    strokeWidth = 2,
    absoluteStrokeWidth,
    className = "",
    children,
    iconNode,
    ...rest
  }, ref) => {
    return reactExports.createElement(
      "svg",
      {
        ref,
        ...defaultAttributes,
        width: size,
        height: size,
        stroke: color,
        strokeWidth: absoluteStrokeWidth ? Number(strokeWidth) * 24 / Number(size) : strokeWidth,
        className: mergeClasses("lucide", className),
        ...rest
      },
      [
        ...iconNode.map(([tag, attrs]) => reactExports.createElement(tag, attrs)),
        ...Array.isArray(children) ? children : [children]
      ]
    );
  }
);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const createLucideIcon = (iconName, iconNode) => {
  const Component = reactExports.forwardRef(
    ({ className, ...props }, ref) => reactExports.createElement(Icon, {
      ref,
      iconNode,
      className: mergeClasses(`lucide-${toKebabCase(iconName)}`, className),
      ...props
    })
  );
  Component.displayName = `${iconName}`;
  return Component;
};
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Activity = createLucideIcon("Activity", [
  [
    "path",
    {
      d: "M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",
      key: "169zse"
    }
  ]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ArrowDown = createLucideIcon("ArrowDown", [
  ["path", { d: "M12 5v14", key: "s699le" }],
  ["path", { d: "m19 12-7 7-7-7", key: "1idqje" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ArrowLeft = createLucideIcon("ArrowLeft", [
  ["path", { d: "m12 19-7-7 7-7", key: "1l729n" }],
  ["path", { d: "M19 12H5", key: "x3x0zl" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ArrowRight = createLucideIcon("ArrowRight", [
  ["path", { d: "M5 12h14", key: "1ays0h" }],
  ["path", { d: "m12 5 7 7-7 7", key: "xquz4c" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Barcode = createLucideIcon("Barcode", [
  ["path", { d: "M3 5v14", key: "1nt18q" }],
  ["path", { d: "M8 5v14", key: "1ybrkv" }],
  ["path", { d: "M12 5v14", key: "s699le" }],
  ["path", { d: "M17 5v14", key: "ycjyhj" }],
  ["path", { d: "M21 5v14", key: "nzette" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Bell = createLucideIcon("Bell", [
  ["path", { d: "M10.268 21a2 2 0 0 0 3.464 0", key: "vwvbt9" }],
  [
    "path",
    {
      d: "M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326",
      key: "11g9vi"
    }
  ]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Bug = createLucideIcon("Bug", [
  ["path", { d: "m8 2 1.88 1.88", key: "fmnt4t" }],
  ["path", { d: "M14.12 3.88 16 2", key: "qol33r" }],
  ["path", { d: "M9 7.13v-1a3.003 3.003 0 1 1 6 0v1", key: "d7y7pr" }],
  [
    "path",
    {
      d: "M12 20c-3.3 0-6-2.7-6-6v-3a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v3c0 3.3-2.7 6-6 6",
      key: "xs1cw7"
    }
  ],
  ["path", { d: "M12 20v-9", key: "1qisl0" }],
  ["path", { d: "M6.53 9C4.6 8.8 3 7.1 3 5", key: "32zzws" }],
  ["path", { d: "M6 13H2", key: "82j7cp" }],
  ["path", { d: "M3 21c0-2.1 1.7-3.9 3.8-4", key: "4p0ekp" }],
  ["path", { d: "M20.97 5c0 2.1-1.6 3.8-3.5 4", key: "18gb23" }],
  ["path", { d: "M22 13h-4", key: "1jl80f" }],
  ["path", { d: "M17.2 17c2.1.1 3.8 1.9 3.8 4", key: "k3fwyw" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const CheckCheck = createLucideIcon("CheckCheck", [
  ["path", { d: "M18 6 7 17l-5-5", key: "116fxf" }],
  ["path", { d: "m22 10-7.5 7.5L13 16", key: "ke71qq" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Check = createLucideIcon("Check", [["path", { d: "M20 6 9 17l-5-5", key: "1gmf2c" }]]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ChevronDown = createLucideIcon("ChevronDown", [
  ["path", { d: "m6 9 6 6 6-6", key: "qrunsl" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ChevronLeft = createLucideIcon("ChevronLeft", [
  ["path", { d: "m15 18-6-6 6-6", key: "1wnfg3" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ChevronRight = createLucideIcon("ChevronRight", [
  ["path", { d: "m9 18 6-6-6-6", key: "mthhwq" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ChevronUp = createLucideIcon("ChevronUp", [["path", { d: "m18 15-6-6-6 6", key: "153udz" }]]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const CircleAlert = createLucideIcon("CircleAlert", [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["line", { x1: "12", x2: "12", y1: "8", y2: "12", key: "1pkeuh" }],
  ["line", { x1: "12", x2: "12.01", y1: "16", y2: "16", key: "4dfq90" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const CircleCheckBig = createLucideIcon("CircleCheckBig", [
  ["path", { d: "M21.801 10A10 10 0 1 1 17 3.335", key: "yps3ct" }],
  ["path", { d: "m9 11 3 3L22 4", key: "1pflzl" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const CircleCheck = createLucideIcon("CircleCheck", [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["path", { d: "m9 12 2 2 4-4", key: "dzmm74" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const CircleStop = createLucideIcon("CircleStop", [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["rect", { x: "9", y: "9", width: "6", height: "6", rx: "1", key: "1ssd4o" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const CircleX = createLucideIcon("CircleX", [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["path", { d: "m15 9-6 6", key: "1uzhvr" }],
  ["path", { d: "m9 9 6 6", key: "z0biqf" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Circle = createLucideIcon("Circle", [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Clock = createLucideIcon("Clock", [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["polyline", { points: "12 6 12 12 16 14", key: "68esgv" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Cloud = createLucideIcon("Cloud", [
  ["path", { d: "M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z", key: "p7xjir" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Copy = createLucideIcon("Copy", [
  ["rect", { width: "14", height: "14", x: "8", y: "8", rx: "2", ry: "2", key: "17jyea" }],
  ["path", { d: "M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2", key: "zix9uf" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Cpu = createLucideIcon("Cpu", [
  ["rect", { width: "16", height: "16", x: "4", y: "4", rx: "2", key: "14l7u7" }],
  ["rect", { width: "6", height: "6", x: "9", y: "9", rx: "1", key: "5aljv4" }],
  ["path", { d: "M15 2v2", key: "13l42r" }],
  ["path", { d: "M15 20v2", key: "15mkzm" }],
  ["path", { d: "M2 15h2", key: "1gxd5l" }],
  ["path", { d: "M2 9h2", key: "1bbxkp" }],
  ["path", { d: "M20 15h2", key: "19e6y8" }],
  ["path", { d: "M20 9h2", key: "19tzq7" }],
  ["path", { d: "M9 2v2", key: "165o2o" }],
  ["path", { d: "M9 20v2", key: "i2bqo8" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Database = createLucideIcon("Database", [
  ["ellipse", { cx: "12", cy: "5", rx: "9", ry: "3", key: "msslwz" }],
  ["path", { d: "M3 5V19A9 3 0 0 0 21 19V5", key: "1wlel7" }],
  ["path", { d: "M3 12A9 3 0 0 0 21 12", key: "mv7ke4" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Download = createLucideIcon("Download", [
  ["path", { d: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4", key: "ih7n3h" }],
  ["polyline", { points: "7 10 12 15 17 10", key: "2ggqvy" }],
  ["line", { x1: "12", x2: "12", y1: "15", y2: "3", key: "1vk2je" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Eye = createLucideIcon("Eye", [
  [
    "path",
    {
      d: "M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0",
      key: "1nclc0"
    }
  ],
  ["circle", { cx: "12", cy: "12", r: "3", key: "1v7zrd" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const FastForward = createLucideIcon("FastForward", [
  ["polygon", { points: "13 19 22 12 13 5 13 19", key: "587y9g" }],
  ["polygon", { points: "2 19 11 12 2 5 2 19", key: "3pweh0" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const FileArchive = createLucideIcon("FileArchive", [
  ["path", { d: "M10 12v-1", key: "v7bkov" }],
  ["path", { d: "M10 18v-2", key: "1cjy8d" }],
  ["path", { d: "M10 7V6", key: "dljcrl" }],
  ["path", { d: "M14 2v4a2 2 0 0 0 2 2h4", key: "tnqrlb" }],
  [
    "path",
    { d: "M15.5 22H18a2 2 0 0 0 2-2V7l-5-5H6a2 2 0 0 0-2 2v16a2 2 0 0 0 .274 1.01", key: "gkbcor" }
  ],
  ["circle", { cx: "10", cy: "20", r: "2", key: "1xzdoj" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const FileText = createLucideIcon("FileText", [
  ["path", { d: "M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z", key: "1rqfz7" }],
  ["path", { d: "M14 2v4a2 2 0 0 0 2 2h4", key: "tnqrlb" }],
  ["path", { d: "M10 9H8", key: "b1mrlr" }],
  ["path", { d: "M16 13H8", key: "t4e002" }],
  ["path", { d: "M16 17H8", key: "z1uh3a" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Filter = createLucideIcon("Filter", [
  ["polygon", { points: "22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3", key: "1yg77f" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Folder = createLucideIcon("Folder", [
  [
    "path",
    {
      d: "M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z",
      key: "1kt360"
    }
  ]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Gauge = createLucideIcon("Gauge", [
  ["path", { d: "m12 14 4-4", key: "9kzdfg" }],
  ["path", { d: "M3.34 19a10 10 0 1 1 17.32 0", key: "19p75a" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const GitBranch = createLucideIcon("GitBranch", [
  ["line", { x1: "6", x2: "6", y1: "3", y2: "15", key: "17qcm7" }],
  ["circle", { cx: "18", cy: "6", r: "3", key: "1h7g24" }],
  ["circle", { cx: "6", cy: "18", r: "3", key: "fqmcym" }],
  ["path", { d: "M18 9a9 9 0 0 1-9 9", key: "n2h4wq" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const GripVertical = createLucideIcon("GripVertical", [
  ["circle", { cx: "9", cy: "12", r: "1", key: "1vctgf" }],
  ["circle", { cx: "9", cy: "5", r: "1", key: "hp0tcf" }],
  ["circle", { cx: "9", cy: "19", r: "1", key: "fkjjf6" }],
  ["circle", { cx: "15", cy: "12", r: "1", key: "1tmaij" }],
  ["circle", { cx: "15", cy: "5", r: "1", key: "19l28e" }],
  ["circle", { cx: "15", cy: "19", r: "1", key: "f4zoj3" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const History = createLucideIcon("History", [
  ["path", { d: "M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8", key: "1357e3" }],
  ["path", { d: "M3 3v5h5", key: "1xhq8a" }],
  ["path", { d: "M12 7v5l4 2", key: "1fdv2h" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const House = createLucideIcon("House", [
  ["path", { d: "M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8", key: "5wwlr5" }],
  [
    "path",
    {
      d: "M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
      key: "1d0kgt"
    }
  ]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Info = createLucideIcon("Info", [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["path", { d: "M12 16v-4", key: "1dtifu" }],
  ["path", { d: "M12 8h.01", key: "e9boi3" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Layers = createLucideIcon("Layers", [
  [
    "path",
    {
      d: "M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z",
      key: "zw3jo"
    }
  ],
  [
    "path",
    {
      d: "M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12",
      key: "1wduqc"
    }
  ],
  [
    "path",
    {
      d: "M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17",
      key: "kqbvx6"
    }
  ]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const LayoutDashboard = createLucideIcon("LayoutDashboard", [
  ["rect", { width: "7", height: "9", x: "3", y: "3", rx: "1", key: "10lvy0" }],
  ["rect", { width: "7", height: "5", x: "14", y: "3", rx: "1", key: "16une8" }],
  ["rect", { width: "7", height: "9", x: "14", y: "12", rx: "1", key: "1hutg5" }],
  ["rect", { width: "7", height: "5", x: "3", y: "16", rx: "1", key: "ldoo1y" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ListOrdered = createLucideIcon("ListOrdered", [
  ["path", { d: "M10 12h11", key: "6m4ad9" }],
  ["path", { d: "M10 18h11", key: "11hvi2" }],
  ["path", { d: "M10 6h11", key: "c7qv1k" }],
  ["path", { d: "M4 10h2", key: "16xx2s" }],
  ["path", { d: "M4 6h1v4", key: "cnovpq" }],
  ["path", { d: "M6 18H4c0-1 2-2 2-3s-1-1.5-2-1", key: "m9a95d" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const LoaderCircle = createLucideIcon("LoaderCircle", [
  ["path", { d: "M21 12a9 9 0 1 1-6.219-8.56", key: "13zald" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const LogIn = createLucideIcon("LogIn", [
  ["path", { d: "M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4", key: "u53s6r" }],
  ["polyline", { points: "10 17 15 12 10 7", key: "1ail0h" }],
  ["line", { x1: "15", x2: "3", y1: "12", y2: "12", key: "v6grx8" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const LogOut = createLucideIcon("LogOut", [
  ["path", { d: "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4", key: "1uf3rs" }],
  ["polyline", { points: "16 17 21 12 16 7", key: "1gabdz" }],
  ["line", { x1: "21", x2: "9", y1: "12", y2: "12", key: "1uyos4" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Minus = createLucideIcon("Minus", [["path", { d: "M5 12h14", key: "1ays0h" }]]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Moon = createLucideIcon("Moon", [
  ["path", { d: "M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z", key: "a7tn18" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Package = createLucideIcon("Package", [
  [
    "path",
    {
      d: "M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z",
      key: "1a0edw"
    }
  ],
  ["path", { d: "M12 22V12", key: "d0xqtd" }],
  ["path", { d: "m3.3 7 7.703 4.734a2 2 0 0 0 1.994 0L20.7 7", key: "yx3hmr" }],
  ["path", { d: "m7.5 4.27 9 5.15", key: "1c824w" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const PanelLeftClose = createLucideIcon("PanelLeftClose", [
  ["rect", { width: "18", height: "18", x: "3", y: "3", rx: "2", key: "afitv7" }],
  ["path", { d: "M9 3v18", key: "fh3hqa" }],
  ["path", { d: "m16 15-3-3 3-3", key: "14y99z" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const PanelLeft = createLucideIcon("PanelLeft", [
  ["rect", { width: "18", height: "18", x: "3", y: "3", rx: "2", key: "afitv7" }],
  ["path", { d: "M9 3v18", key: "fh3hqa" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const PanelRightClose = createLucideIcon("PanelRightClose", [
  ["rect", { width: "18", height: "18", x: "3", y: "3", rx: "2", key: "afitv7" }],
  ["path", { d: "M15 3v18", key: "14nvp0" }],
  ["path", { d: "m8 9 3 3-3 3", key: "12hl5m" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const PanelRightOpen = createLucideIcon("PanelRightOpen", [
  ["rect", { width: "18", height: "18", x: "3", y: "3", rx: "2", key: "afitv7" }],
  ["path", { d: "M15 3v18", key: "14nvp0" }],
  ["path", { d: "m10 15-3-3 3-3", key: "1pgupc" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Pause = createLucideIcon("Pause", [
  ["rect", { x: "14", y: "4", width: "4", height: "16", rx: "1", key: "zuxfzm" }],
  ["rect", { x: "6", y: "4", width: "4", height: "16", rx: "1", key: "1okwgv" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Pen = createLucideIcon("Pen", [
  [
    "path",
    {
      d: "M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z",
      key: "1a8usu"
    }
  ]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Play = createLucideIcon("Play", [
  ["polygon", { points: "6 3 20 12 6 21 6 3", key: "1oa8hb" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Plus = createLucideIcon("Plus", [
  ["path", { d: "M5 12h14", key: "1ays0h" }],
  ["path", { d: "M12 5v14", key: "s699le" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const RefreshCw = createLucideIcon("RefreshCw", [
  ["path", { d: "M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8", key: "v9h5vc" }],
  ["path", { d: "M21 3v5h-5", key: "1q7to0" }],
  ["path", { d: "M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16", key: "3uifl3" }],
  ["path", { d: "M8 16H3v5", key: "1cv678" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const RotateCcw = createLucideIcon("RotateCcw", [
  ["path", { d: "M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8", key: "1357e3" }],
  ["path", { d: "M3 3v5h5", key: "1xhq8a" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Save = createLucideIcon("Save", [
  [
    "path",
    {
      d: "M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z",
      key: "1c8476"
    }
  ],
  ["path", { d: "M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7", key: "1ydtos" }],
  ["path", { d: "M7 3v4a1 1 0 0 0 1 1h7", key: "t51u73" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ScanBarcode = createLucideIcon("ScanBarcode", [
  ["path", { d: "M3 7V5a2 2 0 0 1 2-2h2", key: "aa7l1z" }],
  ["path", { d: "M17 3h2a2 2 0 0 1 2 2v2", key: "4qcy5o" }],
  ["path", { d: "M21 17v2a2 2 0 0 1-2 2h-2", key: "6vwrx8" }],
  ["path", { d: "M7 21H5a2 2 0 0 1-2-2v-2", key: "ioqczr" }],
  ["path", { d: "M8 7v10", key: "23sfjj" }],
  ["path", { d: "M12 7v10", key: "jspqdw" }],
  ["path", { d: "M17 7v10", key: "578dap" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Search = createLucideIcon("Search", [
  ["circle", { cx: "11", cy: "11", r: "8", key: "4ej97u" }],
  ["path", { d: "m21 21-4.3-4.3", key: "1qie3q" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Send = createLucideIcon("Send", [
  [
    "path",
    {
      d: "M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z",
      key: "1ffxy3"
    }
  ],
  ["path", { d: "m21.854 2.147-10.94 10.939", key: "12cjpa" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ServerOff = createLucideIcon("ServerOff", [
  ["path", { d: "M7 2h13a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-5", key: "bt2siv" }],
  ["path", { d: "M10 10 2.5 2.5C2 2 2 2.5 2 5v3a2 2 0 0 0 2 2h6z", key: "1hjrv1" }],
  ["path", { d: "M22 17v-1a2 2 0 0 0-2-2h-1", key: "1iynyr" }],
  ["path", { d: "M4 14a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h16.5l1-.5.5.5-8-8H4z", key: "161ggg" }],
  ["path", { d: "M6 18h.01", key: "uhywen" }],
  ["path", { d: "m2 2 20 20", key: "1ooewy" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Server = createLucideIcon("Server", [
  ["rect", { width: "20", height: "8", x: "2", y: "2", rx: "2", ry: "2", key: "ngkwjq" }],
  ["rect", { width: "20", height: "8", x: "2", y: "14", rx: "2", ry: "2", key: "iecqi9" }],
  ["line", { x1: "6", x2: "6.01", y1: "6", y2: "6", key: "16zg32" }],
  ["line", { x1: "6", x2: "6.01", y1: "18", y2: "18", key: "nzw8ys" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Settings2 = createLucideIcon("Settings2", [
  ["path", { d: "M20 7h-9", key: "3s1dr2" }],
  ["path", { d: "M14 17H5", key: "gfn3mx" }],
  ["circle", { cx: "17", cy: "17", r: "3", key: "18b49y" }],
  ["circle", { cx: "7", cy: "7", r: "3", key: "dfmy0x" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Settings = createLucideIcon("Settings", [
  [
    "path",
    {
      d: "M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z",
      key: "1qme2f"
    }
  ],
  ["circle", { cx: "12", cy: "12", r: "3", key: "1v7zrd" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const SkipForward = createLucideIcon("SkipForward", [
  ["polygon", { points: "5 4 15 12 5 20 5 4", key: "16p6eg" }],
  ["line", { x1: "19", x2: "19", y1: "5", y2: "19", key: "futhcm" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const SlidersVertical = createLucideIcon("SlidersVertical", [
  ["line", { x1: "4", x2: "4", y1: "21", y2: "14", key: "1p332r" }],
  ["line", { x1: "4", x2: "4", y1: "10", y2: "3", key: "gb41h5" }],
  ["line", { x1: "12", x2: "12", y1: "21", y2: "12", key: "hf2csr" }],
  ["line", { x1: "12", x2: "12", y1: "8", y2: "3", key: "1kfi7u" }],
  ["line", { x1: "20", x2: "20", y1: "21", y2: "16", key: "1lhrwl" }],
  ["line", { x1: "20", x2: "20", y1: "12", y2: "3", key: "16vvfq" }],
  ["line", { x1: "2", x2: "6", y1: "14", y2: "14", key: "1uebub" }],
  ["line", { x1: "10", x2: "14", y1: "8", y2: "8", key: "1yglbp" }],
  ["line", { x1: "18", x2: "22", y1: "16", y2: "16", key: "1jxqpz" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Square = createLucideIcon("Square", [
  ["rect", { width: "18", height: "18", x: "3", y: "3", rx: "2", key: "afitv7" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Sun = createLucideIcon("Sun", [
  ["circle", { cx: "12", cy: "12", r: "4", key: "4exip2" }],
  ["path", { d: "M12 2v2", key: "tus03m" }],
  ["path", { d: "M12 20v2", key: "1lh1kg" }],
  ["path", { d: "m4.93 4.93 1.41 1.41", key: "149t6j" }],
  ["path", { d: "m17.66 17.66 1.41 1.41", key: "ptbguv" }],
  ["path", { d: "M2 12h2", key: "1t8f8n" }],
  ["path", { d: "M20 12h2", key: "1q8mjw" }],
  ["path", { d: "m6.34 17.66-1.41 1.41", key: "1m8zz5" }],
  ["path", { d: "m19.07 4.93-1.41 1.41", key: "1shlcs" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Trash2 = createLucideIcon("Trash2", [
  ["path", { d: "M3 6h18", key: "d0wm0j" }],
  ["path", { d: "M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6", key: "4alrt4" }],
  ["path", { d: "M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2", key: "v07s0e" }],
  ["line", { x1: "10", x2: "10", y1: "11", y2: "17", key: "1uufr5" }],
  ["line", { x1: "14", x2: "14", y1: "11", y2: "17", key: "xtxkd" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const TrendingUp = createLucideIcon("TrendingUp", [
  ["polyline", { points: "22 7 13.5 15.5 8.5 10.5 2 17", key: "126l90" }],
  ["polyline", { points: "16 7 22 7 22 13", key: "kwv8wd" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const TriangleAlert = createLucideIcon("TriangleAlert", [
  [
    "path",
    {
      d: "m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3",
      key: "wmoenq"
    }
  ],
  ["path", { d: "M12 9v4", key: "juzpu7" }],
  ["path", { d: "M12 17h.01", key: "p32p05" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Upload = createLucideIcon("Upload", [
  ["path", { d: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4", key: "ih7n3h" }],
  ["polyline", { points: "17 8 12 3 7 8", key: "t8dd8p" }],
  ["line", { x1: "12", x2: "12", y1: "3", y2: "15", key: "widbto" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const User = createLucideIcon("User", [
  ["path", { d: "M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2", key: "975kel" }],
  ["circle", { cx: "12", cy: "7", r: "4", key: "17ys0d" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const WifiOff = createLucideIcon("WifiOff", [
  ["path", { d: "M12 20h.01", key: "zekei9" }],
  ["path", { d: "M8.5 16.429a5 5 0 0 1 7 0", key: "1bycff" }],
  ["path", { d: "M5 12.859a10 10 0 0 1 5.17-2.69", key: "1dl1wf" }],
  ["path", { d: "M19 12.859a10 10 0 0 0-2.007-1.523", key: "4k23kn" }],
  ["path", { d: "M2 8.82a15 15 0 0 1 4.177-2.643", key: "1grhjp" }],
  ["path", { d: "M22 8.82a15 15 0 0 0-11.288-3.764", key: "z3jwby" }],
  ["path", { d: "m2 2 20 20", key: "1ooewy" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Wifi = createLucideIcon("Wifi", [
  ["path", { d: "M12 20h.01", key: "zekei9" }],
  ["path", { d: "M2 8.82a15 15 0 0 1 20 0", key: "dnpr2z" }],
  ["path", { d: "M5 12.859a10 10 0 0 1 14 0", key: "1x1e6c" }],
  ["path", { d: "M8.5 16.429a5 5 0 0 1 7 0", key: "1bycff" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Wrench = createLucideIcon("Wrench", [
  [
    "path",
    {
      d: "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z",
      key: "cbrjhi"
    }
  ]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const X = createLucideIcon("X", [
  ["path", { d: "M18 6 6 18", key: "1bl5f8" }],
  ["path", { d: "m6 6 12 12", key: "d8bk6v" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Zap = createLucideIcon("Zap", [
  [
    "path",
    {
      d: "M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z",
      key: "1xq2db"
    }
  ]
]);
const ROUTES = {
  DASHBOARD: "/",
  BATCHES: "/batches",
  BATCH_DETAIL: "/batches/:batchId",
  SEQUENCES: "/sequences",
  SEQUENCE_DETAIL: "/sequences/:sequenceName",
  MANUAL: "/manual",
  LOGS: "/logs",
  MONITOR: "/monitor",
  SETTINGS: "/settings"
};
function getBatchDetailRoute(batchId) {
  return `/batches/${batchId}`;
}
function getSequenceDetailRoute(sequenceName) {
  return `/sequences/${sequenceName}`;
}
const useConnectionStore = create((set) => ({
  // Initial state
  websocketStatus: "disconnected",
  backendStatus: "disconnected",
  lastHeartbeat: null,
  reconnectAttempts: 0,
  pollingFallbackActive: false,
  // Actions
  setWebSocketStatus: (status) => set({ websocketStatus: status }),
  setBackendStatus: (status) => set({ backendStatus: status }),
  updateHeartbeat: () => set({ lastHeartbeat: /* @__PURE__ */ new Date() }),
  incrementReconnectAttempts: () => set((state) => ({ reconnectAttempts: state.reconnectAttempts + 1 })),
  resetReconnectAttempts: () => set({ reconnectAttempts: 0 }),
  setPollingFallbackActive: (active) => set({ pollingFallbackActive: active })
}));
const navSections = [
  {
    sectionLabel: "MAIN",
    items: [
      { path: ROUTES.DASHBOARD, label: "Dashboard", icon: LayoutDashboard },
      { path: ROUTES.BATCHES, label: "Batches", icon: Layers }
    ]
  },
  {
    sectionLabel: "OPERATIONS",
    items: [
      { path: ROUTES.SEQUENCES, label: "Sequences", icon: GitBranch },
      { path: ROUTES.MANUAL, label: "Manual Control", icon: Wrench }
    ]
  },
  {
    sectionLabel: "SYSTEM",
    items: [
      { path: ROUTES.LOGS, label: "Logs", icon: FileText },
      { path: ROUTES.MONITOR, label: "Monitor", icon: Activity },
      { path: ROUTES.SETTINGS, label: "Settings", icon: Settings }
    ]
  }
];
function Sidebar({ isCollapsed, onToggle, stationId, stationName }) {
  const location = useLocation();
  const [searchQuery, setSearchQuery] = reactExports.useState("");
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  reactExports.useEffect(() => {
    localStorage.setItem("station-sidebar-collapsed", JSON.stringify(isCollapsed));
  }, [isCollapsed]);
  const isActive = (path) => {
    if (location.pathname === path) return true;
    if (path !== "/" && location.pathname.startsWith(path)) return true;
    return false;
  };
  const renderNavItem = (item) => {
    const itemActive = isActive(item.path);
    return /* @__PURE__ */ jsxRuntimeExports.jsxs(
      NavLink,
      {
        to: item.path,
        title: isCollapsed ? item.label : void 0,
        className: `sidebar-nav-item flex items-center gap-3 px-4 py-2.5 mx-3 rounded-lg text-sm font-medium transition-all duration-200 ${isCollapsed ? "justify-center mx-2 px-3" : ""}`,
        style: {
          backgroundColor: itemActive ? "var(--color-brand-500)" : "transparent",
          color: itemActive ? "#ffffff" : "var(--color-text-secondary)"
        },
        onMouseEnter: (e) => {
          if (!itemActive) {
            e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
            e.currentTarget.style.color = "var(--color-text-primary)";
          }
        },
        onMouseLeave: (e) => {
          if (!itemActive) {
            e.currentTarget.style.backgroundColor = "transparent";
            e.currentTarget.style.color = "var(--color-text-secondary)";
          }
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(item.icon, { className: `w-[18px] h-[18px] flex-shrink-0 ${itemActive ? "opacity-100" : "opacity-80"}` }),
          !isCollapsed && /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "flex-1 whitespace-nowrap overflow-hidden text-ellipsis", children: item.label })
        ]
      },
      item.path
    );
  };
  const renderSection = (section) => {
    return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "div",
        {
          className: `px-4 py-2 text-[11px] font-semibold uppercase tracking-wide ${isCollapsed ? "text-center px-0" : "ml-3"}`,
          style: { color: "var(--color-text-tertiary)" },
          children: isCollapsed ? section.sectionLabel.charAt(0) : section.sectionLabel
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-1", children: section.items.map((item) => renderNavItem(item)) })
    ] }, section.sectionLabel);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "aside",
    {
      className: `sidebar flex flex-col h-screen transition-all duration-300 ${isCollapsed ? "w-[72px]" : "w-[260px]"}`,
      style: {
        backgroundColor: "var(--color-bg-secondary)",
        borderRight: "1px solid var(--color-border-default)"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "flex items-center justify-between p-4 min-h-[64px]",
            style: { borderBottom: "1px solid var(--color-border-default)" },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "div",
                  {
                    className: "w-9 h-9 rounded-[10px] flex items-center justify-center flex-shrink-0",
                    style: { backgroundColor: "var(--color-brand-500)" },
                    children: /* @__PURE__ */ jsxRuntimeExports.jsx(Activity, { className: "w-5 h-5 text-white" })
                  }
                ),
                !isCollapsed && /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "span",
                  {
                    className: "font-semibold whitespace-nowrap",
                    style: { color: "var(--color-text-primary)" },
                    children: "Station UI"
                  }
                )
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "button",
                {
                  onClick: onToggle,
                  className: "p-2 rounded-lg transition-colors flex-shrink-0",
                  style: { color: "var(--color-text-secondary)" },
                  onMouseEnter: (e) => {
                    e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
                    e.currentTarget.style.color = "var(--color-text-primary)";
                  },
                  onMouseLeave: (e) => {
                    e.currentTarget.style.backgroundColor = "transparent";
                    e.currentTarget.style.color = "var(--color-text-secondary)";
                  },
                  title: isCollapsed ? "Expand sidebar" : "Collapse sidebar",
                  children: isCollapsed ? /* @__PURE__ */ jsxRuntimeExports.jsx(PanelLeft, { className: "w-5 h-5" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(PanelLeftClose, { className: "w-5 h-5" })
                }
              )
            ]
          }
        ),
        !isCollapsed && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "p-4 pb-2", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "flex items-center gap-2 rounded-lg px-3 py-2.5",
            style: {
              backgroundColor: "var(--color-bg-tertiary)",
              border: "1px solid var(--color-border-default)"
            },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Search, { className: "w-4 h-4 flex-shrink-0", style: { color: "var(--color-text-tertiary)" } }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "input",
                {
                  type: "text",
                  placeholder: "Search...",
                  value: searchQuery,
                  onChange: (e) => setSearchQuery(e.target.value),
                  className: "bg-transparent border-none outline-none flex-1 text-sm",
                  style: { color: "var(--color-text-primary)" }
                }
              )
            ]
          }
        ) }),
        isCollapsed && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "py-3 flex justify-center", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
          "div",
          {
            className: "w-10 h-10 rounded-lg flex items-center justify-center cursor-pointer transition-colors",
            style: { backgroundColor: "var(--color-bg-tertiary)" },
            children: /* @__PURE__ */ jsxRuntimeExports.jsx(Search, { className: "w-[18px] h-[18px]", style: { color: "var(--color-text-tertiary)" } })
          }
        ) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("nav", { className: "flex-1 overflow-y-auto overflow-x-hidden py-2", children: navSections.map(renderSection) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "p-4", style: { borderTop: "1px solid var(--color-border-default)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: `flex items-center gap-3 p-2 rounded-[10px] ${isCollapsed ? "justify-center" : ""}`,
            style: { backgroundColor: "var(--color-bg-tertiary)" },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "div",
                {
                  className: "w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0",
                  style: {
                    backgroundColor: websocketStatus === "connected" ? "rgba(62, 207, 142, 0.2)" : "var(--color-bg-elevated)"
                  },
                  children: /* @__PURE__ */ jsxRuntimeExports.jsx(
                    "div",
                    {
                      className: `w-3 h-3 rounded-full ${websocketStatus === "connecting" ? "animate-pulse" : ""}`,
                      style: {
                        backgroundColor: websocketStatus === "connected" ? "var(--color-brand-500)" : websocketStatus === "connecting" ? "var(--color-warning)" : "var(--color-text-disabled)"
                      }
                    }
                  )
                }
              ),
              !isCollapsed && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 min-w-0", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "div",
                  {
                    className: "font-medium text-sm truncate",
                    style: { color: "var(--color-text-primary)" },
                    children: stationName
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "div",
                  {
                    className: "text-xs font-mono truncate",
                    style: { color: "var(--color-text-tertiary)" },
                    children: stationId
                  }
                )
              ] })
            ]
          }
        ) })
      ]
    }
  );
}
const _ToastManager = class _ToastManager {
  constructor() {
  }
  static getInstance() {
    if (!_ToastManager.instance) {
      _ToastManager.instance = new _ToastManager();
    }
    return _ToastManager.instance;
  }
  /**
   * Show a toast notification.
   */
  show(options) {
    const event = new CustomEvent("toast", { detail: options });
    window.dispatchEvent(event);
  }
  /**
   * Show a success toast.
   */
  success(message, duration) {
    this.show({ type: "success", message, duration });
  }
  /**
   * Show an error toast.
   */
  error(message, duration) {
    this.show({ type: "error", message, duration });
  }
  /**
   * Show a warning toast.
   */
  warning(message, duration) {
    this.show({ type: "warning", message, duration });
  }
  /**
   * Show an info toast.
   */
  info(message, duration) {
    this.show({ type: "info", message, duration });
  }
};
__publicField(_ToastManager, "instance");
let ToastManager = _ToastManager;
const toast = ToastManager.getInstance();
function isErrorWithMessage(error) {
  return typeof error === "object" && error !== null && "message" in error && typeof error.message === "string";
}
function getErrorMessage(error) {
  if (isErrorWithMessage(error)) {
    return error.message;
  }
  if (typeof error === "string") {
    return error;
  }
  return "An unknown error occurred";
}
const LOG_LEVELS = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3
};
const DEFAULT_MIN_LEVEL = "info";
function createLogger(config) {
  const { prefix, minLevel = DEFAULT_MIN_LEVEL, timestamps = false } = config;
  const shouldLog = (level) => {
    return LOG_LEVELS[level] >= LOG_LEVELS[minLevel];
  };
  const formatMessage = (message) => {
    const parts = [];
    if (timestamps) {
      parts.push((/* @__PURE__ */ new Date()).toISOString());
    }
    parts.push(`[${prefix}]`);
    parts.push(message);
    return parts.join(" ");
  };
  const truncateId = (id, length = 8) => {
    return id.length > length ? `${id.slice(0, length)}...` : id;
  };
  return {
    debug: (message, ...args) => {
      if (shouldLog("debug")) {
        console.log(formatMessage(message), ...args);
      }
    },
    info: (message, ...args) => {
      if (shouldLog("info")) {
        console.info(formatMessage(message), ...args);
      }
    },
    warn: (message, ...args) => {
      if (shouldLog("warn")) {
        console.warn(formatMessage(message), ...args);
      }
    },
    error: (message, ...args) => {
      if (shouldLog("error")) {
        console.error(formatMessage(message), ...args);
      }
    },
    /** Helper to truncate batch/execution IDs for cleaner logs */
    truncateId,
    /** Helper for logging batch-related events */
    batch: (batchId, action, details) => {
      if (shouldLog("debug")) {
        const detailStr = details ? ` ${Object.entries(details).map(([k, v]) => `${k}=${v}`).join(", ")}` : "";
        console.log(formatMessage(`${action}: ${truncateId(batchId)}${detailStr}`));
      }
    }
  };
}
const wsLogger = createLogger({ prefix: "WS" });
const batchLogger = createLogger({ prefix: "batchStore" });
createLogger({ prefix: "API" });
function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}
const LEGACY_LOCAL_BATCHES_KEY = "station-ui-local-batches";
const LEGACY_LOCAL_STATS_KEY = "station-ui-local-batch-stats";
const LEGACY_LOCAL_STEPS_KEY = "station-ui-local-batch-steps";
function cleanupLegacyLocalBatches() {
  try {
    const removedKeys = [];
    if (localStorage.getItem(LEGACY_LOCAL_BATCHES_KEY)) {
      localStorage.removeItem(LEGACY_LOCAL_BATCHES_KEY);
      removedKeys.push(LEGACY_LOCAL_BATCHES_KEY);
    }
    if (localStorage.getItem(LEGACY_LOCAL_STATS_KEY)) {
      localStorage.removeItem(LEGACY_LOCAL_STATS_KEY);
      removedKeys.push(LEGACY_LOCAL_STATS_KEY);
    }
    if (localStorage.getItem(LEGACY_LOCAL_STEPS_KEY)) {
      localStorage.removeItem(LEGACY_LOCAL_STEPS_KEY);
      removedKeys.push(LEGACY_LOCAL_STEPS_KEY);
    }
    if (removedKeys.length > 0) {
      batchLogger.info("Cleaned up legacy local batch data:", removedKeys);
    }
  } catch (e) {
    batchLogger.warn("Failed to cleanup legacy local batches:", e);
  }
}
cleanupLegacyLocalBatches();
function ensureBatchExists(batches2, batchId, options) {
  const existing = batches2.get(batchId);
  if (existing) {
    return [batches2, existing];
  }
  const newBatches = new Map(batches2);
  const newBatch = {
    id: batchId,
    name: "Loading...",
    status: (options == null ? void 0 : options.status) ?? "running",
    progress: (options == null ? void 0 : options.progress) ?? 0,
    executionId: options == null ? void 0 : options.executionId,
    sequencePackage: "",
    elapsed: 0,
    hardwareConfig: {},
    autoStart: false,
    steps: []
  };
  newBatches.set(batchId, newBatch);
  batchLogger.batch(batchId, "ensureBatchExists: Created minimal batch");
  return [newBatches, newBatch];
}
const useBatchStore = create((set, get) => ({
  // Initial state
  batches: /* @__PURE__ */ new Map(),
  batchesVersion: 0,
  selectedBatchId: null,
  batchStatistics: /* @__PURE__ */ new Map(),
  isWizardOpen: false,
  // Actions
  setBatches: (batches2) => set((state) => {
    const newBatches = /* @__PURE__ */ new Map();
    for (const batch of batches2) {
      const existing = state.batches.get(batch.id);
      if (existing) {
        if (existing.status === "completed" && batch.status !== "completed") {
          batchLogger.batch(batch.id, "setBatches: BLOCKED status regression", { from: existing.status, to: batch.status });
          newBatches.set(batch.id, existing);
          continue;
        }
        if (existing.status === "running" || existing.status === "starting" || existing.status === "stopping") {
          newBatches.set(batch.id, {
            ...batch,
            status: existing.status,
            currentStep: existing.currentStep,
            stepIndex: existing.stepIndex,
            progress: existing.progress,
            lastRunPassed: existing.lastRunPassed,
            executionId: existing.executionId,
            steps: existing.steps || []
            // WebSocket owns steps during execution
          });
          continue;
        }
        if (existing.status === "completed" && batch.status === "completed") {
          const apiSteps = batch.steps || [];
          const existingSteps = existing.steps || [];
          newBatches.set(batch.id, {
            ...batch,
            steps: apiSteps.length > 0 ? apiSteps : existingSteps
          });
          continue;
        }
      }
      newBatches.set(batch.id, batch);
    }
    return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
  }),
  updateBatch: (batch) => set((state) => {
    const newBatches = new Map(state.batches);
    newBatches.set(batch.id, batch);
    return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
  }),
  removeBatch: (batchId) => set((state) => {
    const newBatches = new Map(state.batches);
    newBatches.delete(batchId);
    const newStats = new Map(state.batchStatistics);
    newStats.delete(batchId);
    return { batches: newBatches, batchStatistics: newStats, batchesVersion: state.batchesVersion + 1 };
  }),
  updateBatchStatus: (batchId, status, executionId, elapsed, force) => set((state) => {
    const newBatches = new Map(state.batches);
    const batch = state.batches.get(batchId);
    batchLogger.batch(batchId, "updateBatchStatus", { status, exec: executionId, elapsed, exists: !!batch, currentStatus: batch == null ? void 0 : batch.status, force: !!force });
    if (batch && !force) {
      const currentStatus = batch.status;
      if (currentStatus === "completed" && status !== "completed" && status !== "error" && status !== "starting") {
        batchLogger.batch(batchId, "updateBatchStatus: BLOCKED regression", { from: currentStatus, to: status });
        return state;
      }
      if (currentStatus === "starting" && status === "idle") {
        batchLogger.batch(batchId, "updateBatchStatus: BLOCKED regression (optimistic)", { from: currentStatus, to: status });
        return state;
      }
      if (currentStatus === "stopping" && status === "running") {
        batchLogger.batch(batchId, "updateBatchStatus: BLOCKED regression (optimistic)", { from: currentStatus, to: status });
        return state;
      }
    }
    if (batch) {
      const updates = { status };
      if (status === "completed") {
        updates.progress = 1;
      }
      if (status === "starting" || status === "running" && batch.status !== "running") {
        updates.elapsed = 0;
        updates.progress = 0;
      }
      if (executionId) {
        updates.executionId = executionId;
      }
      if (elapsed !== void 0) {
        updates.elapsed = elapsed;
      }
      newBatches.set(batchId, { ...batch, ...updates });
    } else {
      newBatches.set(batchId, {
        id: batchId,
        name: "Loading...",
        status,
        progress: status === "completed" ? 1 : 0,
        executionId,
        sequencePackage: "",
        elapsed: elapsed ?? 0,
        hardwareConfig: {},
        autoStart: false
      });
    }
    return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
  }),
  setLastRunResult: (batchId, passed) => set((state) => {
    const newBatches = new Map(state.batches);
    const batch = state.batches.get(batchId);
    if (batch) {
      newBatches.set(batchId, { ...batch, lastRunPassed: passed });
    } else {
      newBatches.set(batchId, {
        id: batchId,
        name: "Loading...",
        status: "completed",
        progress: 1,
        lastRunPassed: passed,
        sequencePackage: "",
        elapsed: 0,
        hardwareConfig: {},
        autoStart: false
      });
    }
    return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
  }),
  updateStepProgress: (batchId, currentStep, stepIndex, progress, executionId) => set((state) => {
    const newBatches = new Map(state.batches);
    const batch = state.batches.get(batchId);
    batchLogger.batch(batchId, "updateStepProgress", { step: currentStep, progress: progress.toFixed(2), exec: executionId, exists: !!batch, status: batch == null ? void 0 : batch.status });
    if (batch && executionId && batch.executionId && batch.executionId !== executionId) {
      batchLogger.debug(`IGNORED: executionId mismatch (batch=${batch.executionId}, event=${executionId})`);
      return state;
    }
    if (batch) {
      const newProgress = Math.max(batch.progress, progress);
      if (progress < batch.progress) {
        batchLogger.batch(batchId, "updateStepProgress: BLOCKED progress regression", { from: batch.progress.toFixed(2), to: progress.toFixed(2) });
      }
      newBatches.set(batchId, {
        ...batch,
        currentStep,
        stepIndex,
        progress: newProgress,
        executionId: executionId || batch.executionId
      });
    } else {
      newBatches.set(batchId, {
        id: batchId,
        name: "Loading...",
        status: "running",
        currentStep,
        stepIndex,
        progress,
        executionId,
        sequencePackage: "",
        elapsed: 0,
        hardwareConfig: {},
        autoStart: false
      });
    }
    return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
  }),
  updateStepResult: (batchId, stepResult) => set((state) => {
    const batch = state.batches.get(batchId);
    if (!batch) return state;
    const newBatches = new Map(state.batches);
    newBatches.set(batchId, {
      ...batch,
      stepIndex: stepResult.order,
      progress: (batch.totalSteps ?? 0) > 0 ? stepResult.order / batch.totalSteps : 0
    });
    return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
  }),
  startStep: (batchId, stepName, stepIndex, totalSteps, executionId) => set((state) => {
    const [batchesWithEntry, batch] = ensureBatchExists(
      state.batches,
      batchId,
      { status: "running", executionId }
    );
    if (executionId && batch.executionId && batch.executionId !== executionId) {
      batchLogger.debug("startStep IGNORED: executionId mismatch");
      return state;
    }
    const newBatches = new Map(batchesWithEntry);
    const currentSteps = batch.steps || [];
    const existingIndex = currentSteps.findIndex((s) => s.name === stepName && s.order === stepIndex + 1);
    let newSteps;
    if (existingIndex >= 0) {
      newSteps = [...currentSteps];
      const existingStep = newSteps[existingIndex];
      newSteps[existingIndex] = {
        order: existingStep.order,
        name: existingStep.name,
        status: "running",
        pass: existingStep.pass,
        duration: existingStep.duration,
        result: existingStep.result
      };
    } else {
      newSteps = [
        ...currentSteps,
        {
          order: stepIndex + 1,
          name: stepName,
          status: "running",
          pass: false,
          duration: void 0,
          result: void 0
        }
      ];
    }
    newBatches.set(batchId, {
      ...batch,
      currentStep: stepName,
      stepIndex,
      totalSteps,
      steps: newSteps,
      executionId: executionId || batch.executionId
    });
    batchLogger.batch(batchId, "startStep", { step: stepName, index: stepIndex });
    return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
  }),
  completeStep: (batchId, stepName, stepIndex, duration, pass, result, executionId) => set((state) => {
    const [batchesWithEntry, batch] = ensureBatchExists(
      state.batches,
      batchId,
      { status: "running", executionId }
    );
    if (executionId && batch.executionId && batch.executionId !== executionId) {
      batchLogger.debug("completeStep IGNORED: executionId mismatch");
      return state;
    }
    const newBatches = new Map(batchesWithEntry);
    const currentSteps = batch.steps || [];
    const existingIndex = currentSteps.findIndex((s) => s.name === stepName);
    let newSteps;
    if (existingIndex >= 0) {
      newSteps = [...currentSteps];
      newSteps[existingIndex] = {
        order: stepIndex + 1,
        name: stepName,
        status: "completed",
        pass,
        duration,
        result
      };
    } else {
      newSteps = [
        ...currentSteps,
        {
          order: stepIndex + 1,
          name: stepName,
          status: "completed",
          pass,
          duration,
          result
        }
      ];
    }
    const totalSteps = batch.totalSteps || newSteps.length;
    const completedSteps = newSteps.filter((s) => s.status === "completed").length;
    const progress = totalSteps > 0 ? completedSteps / totalSteps : 0;
    newBatches.set(batchId, {
      ...batch,
      stepIndex: stepIndex + 1,
      steps: newSteps,
      progress,
      executionId: executionId || batch.executionId
    });
    batchLogger.batch(batchId, "completeStep", { step: stepName, pass, progress: progress.toFixed(2) });
    return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
  }),
  clearSteps: (batchId) => set((state) => {
    const batch = state.batches.get(batchId);
    if (!batch) return state;
    const newBatches = new Map(state.batches);
    newBatches.set(batchId, {
      ...batch,
      steps: [],
      stepIndex: 0,
      progress: 0,
      currentStep: void 0
    });
    return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
  }),
  selectBatch: (batchId) => set({ selectedBatchId: batchId }),
  clearBatches: () => set((state) => ({ batches: /* @__PURE__ */ new Map(), batchesVersion: state.batchesVersion + 1 })),
  // Statistics actions
  setBatchStatistics: (batchId, stats) => set((state) => {
    const newStats = new Map(state.batchStatistics);
    newStats.set(batchId, stats);
    return { batchStatistics: newStats };
  }),
  setAllBatchStatistics: (stats) => set({
    batchStatistics: new Map(Object.entries(stats))
  }),
  incrementBatchStats: (batchId, passed) => set((state) => {
    const newStats = new Map(state.batchStatistics);
    const current = newStats.get(batchId) || { total: 0, passCount: 0, fail: 0 };
    const updated = {
      total: current.total + 1,
      passCount: passed ? current.passCount + 1 : current.passCount,
      fail: passed ? current.fail : current.fail + 1,
      passRate: 0,
      // Preserve duration stats from API (will be updated on next API fetch)
      avgDuration: current.avgDuration,
      lastDuration: current.lastDuration
    };
    updated.passRate = updated.total > 0 ? updated.passCount / updated.total : 0;
    newStats.set(batchId, updated);
    return { batchStatistics: newStats };
  }),
  // Wizard actions
  openWizard: () => set({ isWizardOpen: true }),
  closeWizard: () => set({ isWizardOpen: false }),
  // Selectors
  getBatch: (batchId) => {
    const { batches: batches2 } = get();
    return batches2.get(batchId);
  },
  getAllBatches: () => {
    const { batches: batches2 } = get();
    return Array.from(batches2.values());
  },
  getRunningBatches: () => {
    const allBatches = get().getAllBatches();
    return allBatches.filter((b) => b.status === "running");
  },
  getSelectedBatch: () => {
    const { selectedBatchId } = get();
    return selectedBatchId ? get().getBatch(selectedBatchId) : void 0;
  },
  getBatchStats: (batchId) => {
    const { batchStatistics } = get();
    return batchStatistics.get(batchId);
  },
  getTotalStats: () => {
    const { batchStatistics } = get();
    const total = { total: 0, passCount: 0, fail: 0, passRate: 0 };
    batchStatistics.forEach((s) => {
      total.total += s.total;
      total.passCount += s.passCount;
      total.fail += s.fail;
    });
    total.passRate = total.total > 0 ? total.passCount / total.total : 0;
    return total;
  }
}));
const useLogStore = create((set, get) => ({
  // Initial state
  logs: [],
  maxLogs: 1e3,
  filters: {},
  autoScroll: true,
  // Actions
  addLog: (log2) => set((state) => {
    const newLogs = [...state.logs, log2];
    if (newLogs.length > state.maxLogs) {
      return { logs: newLogs.slice(-state.maxLogs) };
    }
    return { logs: newLogs };
  }),
  addLogs: (logs) => set((state) => {
    const newLogs = [...state.logs, ...logs];
    if (newLogs.length > state.maxLogs) {
      return { logs: newLogs.slice(-state.maxLogs) };
    }
    return { logs: newLogs };
  }),
  clearLogs: () => set({ logs: [] }),
  setFilters: (filters) => set({ filters }),
  setAutoScroll: (autoScroll) => set({ autoScroll }),
  setMaxLogs: (maxLogs) => set({ maxLogs }),
  // Selectors
  getFilteredLogs: () => {
    const { logs, filters } = get();
    return logs.filter((log2) => {
      if (filters.batchId && log2.batchId !== filters.batchId) {
        return false;
      }
      if (filters.level && log2.level !== filters.level) {
        return false;
      }
      if (filters.search && !log2.message.toLowerCase().includes(filters.search.toLowerCase())) {
        return false;
      }
      return true;
    });
  }
}));
function createJSONStorage(getStorage, options) {
  let storage;
  try {
    storage = getStorage();
  } catch (e) {
    return;
  }
  const persistStorage = {
    getItem: (name) => {
      var _a;
      const parse = (str2) => {
        if (str2 === null) {
          return null;
        }
        return JSON.parse(str2, void 0);
      };
      const str = (_a = storage.getItem(name)) != null ? _a : null;
      if (str instanceof Promise) {
        return str.then(parse);
      }
      return parse(str);
    },
    setItem: (name, newValue) => storage.setItem(name, JSON.stringify(newValue, void 0)),
    removeItem: (name) => storage.removeItem(name)
  };
  return persistStorage;
}
const toThenable = (fn) => (input) => {
  try {
    const result = fn(input);
    if (result instanceof Promise) {
      return result;
    }
    return {
      then(onFulfilled) {
        return toThenable(onFulfilled)(result);
      },
      catch(_onRejected) {
        return this;
      }
    };
  } catch (e) {
    return {
      then(_onFulfilled) {
        return this;
      },
      catch(onRejected) {
        return toThenable(onRejected)(e);
      }
    };
  }
};
const persistImpl = (config, baseOptions) => (set, get, api) => {
  let options = {
    storage: createJSONStorage(() => localStorage),
    partialize: (state) => state,
    version: 0,
    merge: (persistedState, currentState) => ({
      ...currentState,
      ...persistedState
    }),
    ...baseOptions
  };
  let hasHydrated = false;
  const hydrationListeners = /* @__PURE__ */ new Set();
  const finishHydrationListeners = /* @__PURE__ */ new Set();
  let storage = options.storage;
  if (!storage) {
    return config(
      (...args) => {
        console.warn(
          `[zustand persist middleware] Unable to update item '${options.name}', the given storage is currently unavailable.`
        );
        set(...args);
      },
      get,
      api
    );
  }
  const setItem = () => {
    const state = options.partialize({ ...get() });
    return storage.setItem(options.name, {
      state,
      version: options.version
    });
  };
  const savedSetState = api.setState;
  api.setState = (state, replace) => {
    savedSetState(state, replace);
    return setItem();
  };
  const configResult = config(
    (...args) => {
      set(...args);
      return setItem();
    },
    get,
    api
  );
  api.getInitialState = () => configResult;
  let stateFromStorage;
  const hydrate = () => {
    var _a, _b;
    if (!storage) return;
    hasHydrated = false;
    hydrationListeners.forEach((cb) => {
      var _a2;
      return cb((_a2 = get()) != null ? _a2 : configResult);
    });
    const postRehydrationCallback = ((_b = options.onRehydrateStorage) == null ? void 0 : _b.call(options, (_a = get()) != null ? _a : configResult)) || void 0;
    return toThenable(storage.getItem.bind(storage))(options.name).then((deserializedStorageValue) => {
      if (deserializedStorageValue) {
        if (typeof deserializedStorageValue.version === "number" && deserializedStorageValue.version !== options.version) {
          if (options.migrate) {
            const migration = options.migrate(
              deserializedStorageValue.state,
              deserializedStorageValue.version
            );
            if (migration instanceof Promise) {
              return migration.then((result) => [true, result]);
            }
            return [true, migration];
          }
          console.error(
            `State loaded from storage couldn't be migrated since no migrate function was provided`
          );
        } else {
          return [false, deserializedStorageValue.state];
        }
      }
      return [false, void 0];
    }).then((migrationResult) => {
      var _a2;
      const [migrated, migratedState] = migrationResult;
      stateFromStorage = options.merge(
        migratedState,
        (_a2 = get()) != null ? _a2 : configResult
      );
      set(stateFromStorage, true);
      if (migrated) {
        return setItem();
      }
    }).then(() => {
      postRehydrationCallback == null ? void 0 : postRehydrationCallback(stateFromStorage, void 0);
      stateFromStorage = get();
      hasHydrated = true;
      finishHydrationListeners.forEach((cb) => cb(stateFromStorage));
    }).catch((e) => {
      postRehydrationCallback == null ? void 0 : postRehydrationCallback(void 0, e);
    });
  };
  api.persist = {
    setOptions: (newOptions) => {
      options = {
        ...options,
        ...newOptions
      };
      if (newOptions.storage) {
        storage = newOptions.storage;
      }
    },
    clearStorage: () => {
      storage == null ? void 0 : storage.removeItem(options.name);
    },
    getOptions: () => options,
    rehydrate: () => hydrate(),
    hasHydrated: () => hasHydrated,
    onHydrate: (cb) => {
      hydrationListeners.add(cb);
      return () => {
        hydrationListeners.delete(cb);
      };
    },
    onFinishHydration: (cb) => {
      finishHydrationListeners.add(cb);
      return () => {
        finishHydrationListeners.delete(cb);
      };
    }
  };
  if (!options.skipHydration) {
    hydrate();
  }
  return stateFromStorage || configResult;
};
const persist = persistImpl;
const useUIStore = create()(
  persist(
    (set) => ({
      // Initial state
      theme: "dark",
      sidebarCollapsed: false,
      // Actions
      setTheme: (theme) => {
        if (theme === "dark") {
          document.documentElement.classList.add("dark");
        } else {
          document.documentElement.classList.remove("dark");
        }
        set({ theme });
      },
      toggleTheme: () => set((state) => {
        const newTheme = state.theme === "dark" ? "light" : "dark";
        if (newTheme === "dark") {
          document.documentElement.classList.add("dark");
        } else {
          document.documentElement.classList.remove("dark");
        }
        return { theme: newTheme };
      }),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }))
    }),
    {
      name: "station-ui-settings",
      partialize: (state) => ({ theme: state.theme }),
      onRehydrateStorage: () => (state) => {
        if ((state == null ? void 0 : state.theme) === "dark") {
          document.documentElement.classList.add("dark");
        } else {
          document.documentElement.classList.remove("dark");
        }
      }
    }
  )
);
function generateId$1() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}
const useNotificationStore = create()(
  persist(
    (set, get) => ({
      // Initial state
      notifications: [],
      maxNotifications: 50,
      isOpen: false,
      // Actions
      addNotification: (notification) => set((state) => {
        const newNotification = {
          ...notification,
          id: generateId$1(),
          timestamp: /* @__PURE__ */ new Date(),
          read: false
        };
        const newNotifications = [newNotification, ...state.notifications];
        if (newNotifications.length > state.maxNotifications) {
          return { notifications: newNotifications.slice(0, state.maxNotifications) };
        }
        return { notifications: newNotifications };
      }),
      markAsRead: (id) => set((state) => ({
        notifications: state.notifications.map(
          (n) => n.id === id ? { ...n, read: true } : n
        )
      })),
      markAllAsRead: () => set((state) => ({
        notifications: state.notifications.map((n) => ({ ...n, read: true }))
      })),
      removeNotification: (id) => set((state) => ({
        notifications: state.notifications.filter((n) => n.id !== id)
      })),
      clearAll: () => set({ notifications: [] }),
      setIsOpen: (isOpen) => set({ isOpen }),
      togglePanel: () => set((state) => ({ isOpen: !state.isOpen })),
      // Selectors
      getUnreadCount: () => {
        const { notifications } = get();
        return notifications.filter((n) => !n.read).length;
      }
    }),
    {
      name: "station-ui-notifications",
      partialize: (state) => ({
        notifications: state.notifications.map((n) => ({
          ...n,
          timestamp: n.timestamp.toISOString()
        }))
      }),
      onRehydrateStorage: () => (state) => {
        if (state == null ? void 0 : state.notifications) {
          state.notifications = state.notifications.map((n) => ({
            ...n,
            timestamp: typeof n.timestamp === "string" ? new Date(n.timestamp) : n.timestamp
          }));
        }
      }
    }
  )
);
const typeIcons = {
  info: /* @__PURE__ */ jsxRuntimeExports.jsx(Info, { className: "w-4 h-4" }),
  success: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-4 h-4" }),
  warning: /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-4 h-4" }),
  error: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleAlert, { className: "w-4 h-4" })
};
const typeColors = {
  info: "var(--color-accent-blue)",
  success: "var(--color-status-success)",
  warning: "var(--color-status-warning)",
  error: "var(--color-status-error)"
};
function formatTimestamp$1(date) {
  const now = /* @__PURE__ */ new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 6e4);
  const hours = Math.floor(diff / 36e5);
  const days = Math.floor(diff / 864e5);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}
function NotificationItem({ notification, onMarkAsRead, onRemove }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsx(
    "div",
    {
      className: "px-4 py-3 border-b transition-colors cursor-pointer",
      style: {
        backgroundColor: notification.read ? "transparent" : "var(--color-bg-tertiary)",
        borderColor: "var(--color-border-default)"
      },
      onClick: () => !notification.read && onMarkAsRead(notification.id),
      children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-start gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "div",
          {
            className: "mt-0.5 flex-shrink-0",
            style: { color: typeColors[notification.type] },
            children: typeIcons[notification.type]
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 min-w-0", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between gap-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "span",
              {
                className: "font-medium text-sm truncate",
                style: { color: "var(--color-text-primary)" },
                children: notification.title
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "button",
              {
                onClick: (e) => {
                  e.stopPropagation();
                  onRemove(notification.id);
                },
                className: "p-1 rounded hover:bg-red-500/20 transition-colors flex-shrink-0",
                style: { color: "var(--color-text-tertiary)" },
                title: "Remove notification",
                children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-3 h-3" })
              }
            )
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "p",
            {
              className: "text-xs mt-1 line-clamp-2",
              style: { color: "var(--color-text-secondary)" },
              children: notification.message
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mt-1.5", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "span",
              {
                className: "text-xs",
                style: { color: "var(--color-text-tertiary)" },
                children: formatTimestamp$1(notification.timestamp)
              }
            ),
            !notification.read && /* @__PURE__ */ jsxRuntimeExports.jsx(
              "span",
              {
                className: "w-2 h-2 rounded-full",
                style: { backgroundColor: "var(--color-accent-blue)" }
              }
            )
          ] })
        ] })
      ] })
    }
  );
}
function NotificationPanel() {
  const panelRef = reactExports.useRef(null);
  const {
    notifications,
    isOpen,
    setIsOpen,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    getUnreadCount
  } = useNotificationStore();
  const unreadCount = getUnreadCount();
  reactExports.useEffect(() => {
    function handleClickOutside(event) {
      if (panelRef.current && !panelRef.current.contains(event.target)) {
        const target = event.target;
        if (target.closest("[data-notification-trigger]")) {
          return;
        }
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isOpen, setIsOpen]);
  reactExports.useEffect(() => {
    function handleEscape(event) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      return () => document.removeEventListener("keydown", handleEscape);
    }
  }, [isOpen, setIsOpen]);
  if (!isOpen) return null;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      ref: panelRef,
      className: "absolute top-full right-0 mt-2 w-80 max-h-[480px] rounded-lg shadow-xl overflow-hidden z-50",
      style: {
        backgroundColor: "var(--color-bg-secondary)",
        border: "1px solid var(--color-border-default)"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "px-4 py-3 border-b flex items-center justify-between",
            style: { borderColor: "var(--color-border-default)" },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "h3",
                {
                  className: "font-semibold text-sm",
                  style: { color: "var(--color-text-primary)" },
                  children: [
                    "Notifications",
                    unreadCount > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx(
                      "span",
                      {
                        className: "ml-2 px-1.5 py-0.5 text-xs rounded-full",
                        style: {
                          backgroundColor: "var(--color-accent-blue)",
                          color: "white"
                        },
                        children: unreadCount
                      }
                    )
                  ]
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1", children: [
                unreadCount > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "button",
                  {
                    onClick: markAllAsRead,
                    className: "p-1.5 rounded transition-colors",
                    style: { color: "var(--color-text-secondary)" },
                    onMouseEnter: (e) => {
                      e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
                      e.currentTarget.style.color = "var(--color-text-primary)";
                    },
                    onMouseLeave: (e) => {
                      e.currentTarget.style.backgroundColor = "transparent";
                      e.currentTarget.style.color = "var(--color-text-secondary)";
                    },
                    title: "Mark all as read",
                    children: /* @__PURE__ */ jsxRuntimeExports.jsx(CheckCheck, { className: "w-4 h-4" })
                  }
                ),
                notifications.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "button",
                  {
                    onClick: clearAll,
                    className: "p-1.5 rounded transition-colors",
                    style: { color: "var(--color-text-secondary)" },
                    onMouseEnter: (e) => {
                      e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
                      e.currentTarget.style.color = "var(--color-status-error)";
                    },
                    onMouseLeave: (e) => {
                      e.currentTarget.style.backgroundColor = "transparent";
                      e.currentTarget.style.color = "var(--color-text-secondary)";
                    },
                    title: "Clear all notifications",
                    children: /* @__PURE__ */ jsxRuntimeExports.jsx(Trash2, { className: "w-4 h-4" })
                  }
                )
              ] })
            ]
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "max-h-[400px] overflow-y-auto", children: notifications.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "px-4 py-8 text-center",
            style: { color: "var(--color-text-tertiary)" },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Info, { className: "w-8 h-8 mx-auto mb-2 opacity-50" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", children: "No notifications" })
            ]
          }
        ) : notifications.map((notification) => /* @__PURE__ */ jsxRuntimeExports.jsx(
          NotificationItem,
          {
            notification,
            onMarkAsRead: markAsRead,
            onRemove: removeNotification
          },
          notification.id
        )) })
      ]
    }
  );
}
const POLLING_INTERVALS = {
  /** Batch list polling interval (normal mode) */
  batches: 1e4,
  // 10 seconds
  /** Batch list polling interval (fallback mode when WebSocket is disconnected) */
  batchesFallback: 3e3,
  // 3 seconds - faster polling when WS is down
  /** Batch detail polling interval (for real-time step updates) */
  batchDetail: 1e3,
  // 1 second - fast polling for step progress
  /** Health status polling interval */
  health: 3e4,
  // 30 seconds
  /** System info cache time (not polling, just stale time) */
  systemInfo: 6e4
  // 1 minute
};
const QUERY_OPTIONS = {
  /** Default stale time for queries */
  staleTime: 3e4,
  // 30 seconds
  /** Default garbage collection time */
  gcTime: 5 * 6e4,
  // 5 minutes
  /** Default retry count for queries */
  queryRetry: 2,
  /** Default retry count for mutations */
  mutationRetry: 1
};
const WEBSOCKET_CONFIG = {
  /** Reconnection delay in milliseconds */
  reconnectionDelay: 1e3,
  /** Maximum reconnection delay in milliseconds */
  reconnectionDelayMax: 3e4
};
const defaultQueryOptions = {
  queries: {
    staleTime: QUERY_OPTIONS.staleTime,
    gcTime: QUERY_OPTIONS.gcTime,
    retry: QUERY_OPTIONS.queryRetry,
    refetchOnWindowFocus: false,
    refetchOnReconnect: true
  },
  mutations: {
    retry: QUERY_OPTIONS.mutationRetry
  }
};
const queryClient = new QueryClient({
  defaultOptions: defaultQueryOptions
});
const queryKeys = {
  // System
  systemInfo: ["system", "info"],
  healthStatus: ["system", "health"],
  workflowConfig: ["system", "workflow"],
  operatorSession: ["system", "operator"],
  // Batches
  batches: ["batches"],
  batch: (id) => ["batches", id],
  batchStatistics: (id) => ["batchStatistics", id],
  allBatchStatistics: ["batchStatistics"],
  // Sequences
  sequences: ["sequences"],
  sequence: (name) => ["sequences", name],
  // Results
  results: (params) => ["results", params],
  result: (id) => ["results", id],
  // Logs
  logs: (params) => ["logs", params]
};
function bind(fn, thisArg) {
  return function wrap() {
    return fn.apply(thisArg, arguments);
  };
}
const { toString } = Object.prototype;
const { getPrototypeOf } = Object;
const { iterator, toStringTag } = Symbol;
const kindOf = /* @__PURE__ */ ((cache) => (thing) => {
  const str = toString.call(thing);
  return cache[str] || (cache[str] = str.slice(8, -1).toLowerCase());
})(/* @__PURE__ */ Object.create(null));
const kindOfTest = (type) => {
  type = type.toLowerCase();
  return (thing) => kindOf(thing) === type;
};
const typeOfTest = (type) => (thing) => typeof thing === type;
const { isArray } = Array;
const isUndefined = typeOfTest("undefined");
function isBuffer(val) {
  return val !== null && !isUndefined(val) && val.constructor !== null && !isUndefined(val.constructor) && isFunction$1(val.constructor.isBuffer) && val.constructor.isBuffer(val);
}
const isArrayBuffer = kindOfTest("ArrayBuffer");
function isArrayBufferView(val) {
  let result;
  if (typeof ArrayBuffer !== "undefined" && ArrayBuffer.isView) {
    result = ArrayBuffer.isView(val);
  } else {
    result = val && val.buffer && isArrayBuffer(val.buffer);
  }
  return result;
}
const isString = typeOfTest("string");
const isFunction$1 = typeOfTest("function");
const isNumber = typeOfTest("number");
const isObject = (thing) => thing !== null && typeof thing === "object";
const isBoolean = (thing) => thing === true || thing === false;
const isPlainObject = (val) => {
  if (kindOf(val) !== "object") {
    return false;
  }
  const prototype2 = getPrototypeOf(val);
  return (prototype2 === null || prototype2 === Object.prototype || Object.getPrototypeOf(prototype2) === null) && !(toStringTag in val) && !(iterator in val);
};
const isEmptyObject = (val) => {
  if (!isObject(val) || isBuffer(val)) {
    return false;
  }
  try {
    return Object.keys(val).length === 0 && Object.getPrototypeOf(val) === Object.prototype;
  } catch (e) {
    return false;
  }
};
const isDate = kindOfTest("Date");
const isFile = kindOfTest("File");
const isBlob = kindOfTest("Blob");
const isFileList = kindOfTest("FileList");
const isStream = (val) => isObject(val) && isFunction$1(val.pipe);
const isFormData = (thing) => {
  let kind;
  return thing && (typeof FormData === "function" && thing instanceof FormData || isFunction$1(thing.append) && ((kind = kindOf(thing)) === "formdata" || // detect form-data instance
  kind === "object" && isFunction$1(thing.toString) && thing.toString() === "[object FormData]"));
};
const isURLSearchParams = kindOfTest("URLSearchParams");
const [isReadableStream, isRequest, isResponse, isHeaders] = ["ReadableStream", "Request", "Response", "Headers"].map(kindOfTest);
const trim = (str) => str.trim ? str.trim() : str.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g, "");
function forEach(obj, fn, { allOwnKeys = false } = {}) {
  if (obj === null || typeof obj === "undefined") {
    return;
  }
  let i;
  let l;
  if (typeof obj !== "object") {
    obj = [obj];
  }
  if (isArray(obj)) {
    for (i = 0, l = obj.length; i < l; i++) {
      fn.call(null, obj[i], i, obj);
    }
  } else {
    if (isBuffer(obj)) {
      return;
    }
    const keys = allOwnKeys ? Object.getOwnPropertyNames(obj) : Object.keys(obj);
    const len = keys.length;
    let key;
    for (i = 0; i < len; i++) {
      key = keys[i];
      fn.call(null, obj[key], key, obj);
    }
  }
}
function findKey(obj, key) {
  if (isBuffer(obj)) {
    return null;
  }
  key = key.toLowerCase();
  const keys = Object.keys(obj);
  let i = keys.length;
  let _key;
  while (i-- > 0) {
    _key = keys[i];
    if (key === _key.toLowerCase()) {
      return _key;
    }
  }
  return null;
}
const _global = (() => {
  if (typeof globalThis !== "undefined") return globalThis;
  return typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : global;
})();
const isContextDefined = (context) => !isUndefined(context) && context !== _global;
function merge() {
  const { caseless, skipUndefined } = isContextDefined(this) && this || {};
  const result = {};
  const assignValue = (val, key) => {
    const targetKey = caseless && findKey(result, key) || key;
    if (isPlainObject(result[targetKey]) && isPlainObject(val)) {
      result[targetKey] = merge(result[targetKey], val);
    } else if (isPlainObject(val)) {
      result[targetKey] = merge({}, val);
    } else if (isArray(val)) {
      result[targetKey] = val.slice();
    } else if (!skipUndefined || !isUndefined(val)) {
      result[targetKey] = val;
    }
  };
  for (let i = 0, l = arguments.length; i < l; i++) {
    arguments[i] && forEach(arguments[i], assignValue);
  }
  return result;
}
const extend = (a, b, thisArg, { allOwnKeys } = {}) => {
  forEach(b, (val, key) => {
    if (thisArg && isFunction$1(val)) {
      a[key] = bind(val, thisArg);
    } else {
      a[key] = val;
    }
  }, { allOwnKeys });
  return a;
};
const stripBOM = (content) => {
  if (content.charCodeAt(0) === 65279) {
    content = content.slice(1);
  }
  return content;
};
const inherits = (constructor, superConstructor, props, descriptors2) => {
  constructor.prototype = Object.create(superConstructor.prototype, descriptors2);
  constructor.prototype.constructor = constructor;
  Object.defineProperty(constructor, "super", {
    value: superConstructor.prototype
  });
  props && Object.assign(constructor.prototype, props);
};
const toFlatObject = (sourceObj, destObj, filter2, propFilter) => {
  let props;
  let i;
  let prop;
  const merged = {};
  destObj = destObj || {};
  if (sourceObj == null) return destObj;
  do {
    props = Object.getOwnPropertyNames(sourceObj);
    i = props.length;
    while (i-- > 0) {
      prop = props[i];
      if ((!propFilter || propFilter(prop, sourceObj, destObj)) && !merged[prop]) {
        destObj[prop] = sourceObj[prop];
        merged[prop] = true;
      }
    }
    sourceObj = filter2 !== false && getPrototypeOf(sourceObj);
  } while (sourceObj && (!filter2 || filter2(sourceObj, destObj)) && sourceObj !== Object.prototype);
  return destObj;
};
const endsWith = (str, searchString, position) => {
  str = String(str);
  if (position === void 0 || position > str.length) {
    position = str.length;
  }
  position -= searchString.length;
  const lastIndex = str.indexOf(searchString, position);
  return lastIndex !== -1 && lastIndex === position;
};
const toArray = (thing) => {
  if (!thing) return null;
  if (isArray(thing)) return thing;
  let i = thing.length;
  if (!isNumber(i)) return null;
  const arr = new Array(i);
  while (i-- > 0) {
    arr[i] = thing[i];
  }
  return arr;
};
const isTypedArray = /* @__PURE__ */ ((TypedArray) => {
  return (thing) => {
    return TypedArray && thing instanceof TypedArray;
  };
})(typeof Uint8Array !== "undefined" && getPrototypeOf(Uint8Array));
const forEachEntry = (obj, fn) => {
  const generator = obj && obj[iterator];
  const _iterator = generator.call(obj);
  let result;
  while ((result = _iterator.next()) && !result.done) {
    const pair = result.value;
    fn.call(obj, pair[0], pair[1]);
  }
};
const matchAll = (regExp, str) => {
  let matches;
  const arr = [];
  while ((matches = regExp.exec(str)) !== null) {
    arr.push(matches);
  }
  return arr;
};
const isHTMLForm = kindOfTest("HTMLFormElement");
const toCamelCase = (str) => {
  return str.toLowerCase().replace(
    /[-_\s]([a-z\d])(\w*)/g,
    function replacer(m, p1, p2) {
      return p1.toUpperCase() + p2;
    }
  );
};
const hasOwnProperty = (({ hasOwnProperty: hasOwnProperty2 }) => (obj, prop) => hasOwnProperty2.call(obj, prop))(Object.prototype);
const isRegExp = kindOfTest("RegExp");
const reduceDescriptors = (obj, reducer) => {
  const descriptors2 = Object.getOwnPropertyDescriptors(obj);
  const reducedDescriptors = {};
  forEach(descriptors2, (descriptor, name) => {
    let ret;
    if ((ret = reducer(descriptor, name, obj)) !== false) {
      reducedDescriptors[name] = ret || descriptor;
    }
  });
  Object.defineProperties(obj, reducedDescriptors);
};
const freezeMethods = (obj) => {
  reduceDescriptors(obj, (descriptor, name) => {
    if (isFunction$1(obj) && ["arguments", "caller", "callee"].indexOf(name) !== -1) {
      return false;
    }
    const value = obj[name];
    if (!isFunction$1(value)) return;
    descriptor.enumerable = false;
    if ("writable" in descriptor) {
      descriptor.writable = false;
      return;
    }
    if (!descriptor.set) {
      descriptor.set = () => {
        throw Error("Can not rewrite read-only method '" + name + "'");
      };
    }
  });
};
const toObjectSet = (arrayOrString, delimiter) => {
  const obj = {};
  const define = (arr) => {
    arr.forEach((value) => {
      obj[value] = true;
    });
  };
  isArray(arrayOrString) ? define(arrayOrString) : define(String(arrayOrString).split(delimiter));
  return obj;
};
const noop = () => {
};
const toFiniteNumber = (value, defaultValue) => {
  return value != null && Number.isFinite(value = +value) ? value : defaultValue;
};
function isSpecCompliantForm(thing) {
  return !!(thing && isFunction$1(thing.append) && thing[toStringTag] === "FormData" && thing[iterator]);
}
const toJSONObject = (obj) => {
  const stack = new Array(10);
  const visit = (source, i) => {
    if (isObject(source)) {
      if (stack.indexOf(source) >= 0) {
        return;
      }
      if (isBuffer(source)) {
        return source;
      }
      if (!("toJSON" in source)) {
        stack[i] = source;
        const target = isArray(source) ? [] : {};
        forEach(source, (value, key) => {
          const reducedValue = visit(value, i + 1);
          !isUndefined(reducedValue) && (target[key] = reducedValue);
        });
        stack[i] = void 0;
        return target;
      }
    }
    return source;
  };
  return visit(obj, 0);
};
const isAsyncFn = kindOfTest("AsyncFunction");
const isThenable = (thing) => thing && (isObject(thing) || isFunction$1(thing)) && isFunction$1(thing.then) && isFunction$1(thing.catch);
const _setImmediate = ((setImmediateSupported, postMessageSupported) => {
  if (setImmediateSupported) {
    return setImmediate;
  }
  return postMessageSupported ? ((token, callbacks) => {
    _global.addEventListener("message", ({ source, data }) => {
      if (source === _global && data === token) {
        callbacks.length && callbacks.shift()();
      }
    }, false);
    return (cb) => {
      callbacks.push(cb);
      _global.postMessage(token, "*");
    };
  })(`axios@${Math.random()}`, []) : (cb) => setTimeout(cb);
})(
  typeof setImmediate === "function",
  isFunction$1(_global.postMessage)
);
const asap = typeof queueMicrotask !== "undefined" ? queueMicrotask.bind(_global) : typeof process !== "undefined" && process.nextTick || _setImmediate;
const isIterable$1 = (thing) => thing != null && isFunction$1(thing[iterator]);
const utils$1 = {
  isArray,
  isArrayBuffer,
  isBuffer,
  isFormData,
  isArrayBufferView,
  isString,
  isNumber,
  isBoolean,
  isObject,
  isPlainObject,
  isEmptyObject,
  isReadableStream,
  isRequest,
  isResponse,
  isHeaders,
  isUndefined,
  isDate,
  isFile,
  isBlob,
  isRegExp,
  isFunction: isFunction$1,
  isStream,
  isURLSearchParams,
  isTypedArray,
  isFileList,
  forEach,
  merge,
  extend,
  trim,
  stripBOM,
  inherits,
  toFlatObject,
  kindOf,
  kindOfTest,
  endsWith,
  toArray,
  forEachEntry,
  matchAll,
  isHTMLForm,
  hasOwnProperty,
  hasOwnProp: hasOwnProperty,
  // an alias to avoid ESLint no-prototype-builtins detection
  reduceDescriptors,
  freezeMethods,
  toObjectSet,
  toCamelCase,
  noop,
  toFiniteNumber,
  findKey,
  global: _global,
  isContextDefined,
  isSpecCompliantForm,
  toJSONObject,
  isAsyncFn,
  isThenable,
  setImmediate: _setImmediate,
  asap,
  isIterable: isIterable$1
};
function AxiosError$1(message, code, config, request, response) {
  Error.call(this);
  if (Error.captureStackTrace) {
    Error.captureStackTrace(this, this.constructor);
  } else {
    this.stack = new Error().stack;
  }
  this.message = message;
  this.name = "AxiosError";
  code && (this.code = code);
  config && (this.config = config);
  request && (this.request = request);
  if (response) {
    this.response = response;
    this.status = response.status ? response.status : null;
  }
}
utils$1.inherits(AxiosError$1, Error, {
  toJSON: function toJSON() {
    return {
      // Standard
      message: this.message,
      name: this.name,
      // Microsoft
      description: this.description,
      number: this.number,
      // Mozilla
      fileName: this.fileName,
      lineNumber: this.lineNumber,
      columnNumber: this.columnNumber,
      stack: this.stack,
      // Axios
      config: utils$1.toJSONObject(this.config),
      code: this.code,
      status: this.status
    };
  }
});
const prototype$1 = AxiosError$1.prototype;
const descriptors = {};
[
  "ERR_BAD_OPTION_VALUE",
  "ERR_BAD_OPTION",
  "ECONNABORTED",
  "ETIMEDOUT",
  "ERR_NETWORK",
  "ERR_FR_TOO_MANY_REDIRECTS",
  "ERR_DEPRECATED",
  "ERR_BAD_RESPONSE",
  "ERR_BAD_REQUEST",
  "ERR_CANCELED",
  "ERR_NOT_SUPPORT",
  "ERR_INVALID_URL"
  // eslint-disable-next-line func-names
].forEach((code) => {
  descriptors[code] = { value: code };
});
Object.defineProperties(AxiosError$1, descriptors);
Object.defineProperty(prototype$1, "isAxiosError", { value: true });
AxiosError$1.from = (error, code, config, request, response, customProps) => {
  const axiosError = Object.create(prototype$1);
  utils$1.toFlatObject(error, axiosError, function filter2(obj) {
    return obj !== Error.prototype;
  }, (prop) => {
    return prop !== "isAxiosError";
  });
  const msg = error && error.message ? error.message : "Error";
  const errCode = code == null && error ? error.code : code;
  AxiosError$1.call(axiosError, msg, errCode, config, request, response);
  if (error && axiosError.cause == null) {
    Object.defineProperty(axiosError, "cause", { value: error, configurable: true });
  }
  axiosError.name = error && error.name || "Error";
  customProps && Object.assign(axiosError, customProps);
  return axiosError;
};
const httpAdapter = null;
function isVisitable(thing) {
  return utils$1.isPlainObject(thing) || utils$1.isArray(thing);
}
function removeBrackets(key) {
  return utils$1.endsWith(key, "[]") ? key.slice(0, -2) : key;
}
function renderKey(path, key, dots) {
  if (!path) return key;
  return path.concat(key).map(function each(token, i) {
    token = removeBrackets(token);
    return !dots && i ? "[" + token + "]" : token;
  }).join(dots ? "." : "");
}
function isFlatArray(arr) {
  return utils$1.isArray(arr) && !arr.some(isVisitable);
}
const predicates = utils$1.toFlatObject(utils$1, {}, null, function filter(prop) {
  return /^is[A-Z]/.test(prop);
});
function toFormData$1(obj, formData, options) {
  if (!utils$1.isObject(obj)) {
    throw new TypeError("target must be an object");
  }
  formData = formData || new FormData();
  options = utils$1.toFlatObject(options, {
    metaTokens: true,
    dots: false,
    indexes: false
  }, false, function defined(option, source) {
    return !utils$1.isUndefined(source[option]);
  });
  const metaTokens = options.metaTokens;
  const visitor = options.visitor || defaultVisitor;
  const dots = options.dots;
  const indexes = options.indexes;
  const _Blob = options.Blob || typeof Blob !== "undefined" && Blob;
  const useBlob = _Blob && utils$1.isSpecCompliantForm(formData);
  if (!utils$1.isFunction(visitor)) {
    throw new TypeError("visitor must be a function");
  }
  function convertValue(value) {
    if (value === null) return "";
    if (utils$1.isDate(value)) {
      return value.toISOString();
    }
    if (utils$1.isBoolean(value)) {
      return value.toString();
    }
    if (!useBlob && utils$1.isBlob(value)) {
      throw new AxiosError$1("Blob is not supported. Use a Buffer instead.");
    }
    if (utils$1.isArrayBuffer(value) || utils$1.isTypedArray(value)) {
      return useBlob && typeof Blob === "function" ? new Blob([value]) : Buffer.from(value);
    }
    return value;
  }
  function defaultVisitor(value, key, path) {
    let arr = value;
    if (value && !path && typeof value === "object") {
      if (utils$1.endsWith(key, "{}")) {
        key = metaTokens ? key : key.slice(0, -2);
        value = JSON.stringify(value);
      } else if (utils$1.isArray(value) && isFlatArray(value) || (utils$1.isFileList(value) || utils$1.endsWith(key, "[]")) && (arr = utils$1.toArray(value))) {
        key = removeBrackets(key);
        arr.forEach(function each(el, index) {
          !(utils$1.isUndefined(el) || el === null) && formData.append(
            // eslint-disable-next-line no-nested-ternary
            indexes === true ? renderKey([key], index, dots) : indexes === null ? key : key + "[]",
            convertValue(el)
          );
        });
        return false;
      }
    }
    if (isVisitable(value)) {
      return true;
    }
    formData.append(renderKey(path, key, dots), convertValue(value));
    return false;
  }
  const stack = [];
  const exposedHelpers = Object.assign(predicates, {
    defaultVisitor,
    convertValue,
    isVisitable
  });
  function build(value, path) {
    if (utils$1.isUndefined(value)) return;
    if (stack.indexOf(value) !== -1) {
      throw Error("Circular reference detected in " + path.join("."));
    }
    stack.push(value);
    utils$1.forEach(value, function each(el, key) {
      const result = !(utils$1.isUndefined(el) || el === null) && visitor.call(
        formData,
        el,
        utils$1.isString(key) ? key.trim() : key,
        path,
        exposedHelpers
      );
      if (result === true) {
        build(el, path ? path.concat(key) : [key]);
      }
    });
    stack.pop();
  }
  if (!utils$1.isObject(obj)) {
    throw new TypeError("data must be an object");
  }
  build(obj);
  return formData;
}
function encode$1(str) {
  const charMap = {
    "!": "%21",
    "'": "%27",
    "(": "%28",
    ")": "%29",
    "~": "%7E",
    "%20": "+",
    "%00": "\0"
  };
  return encodeURIComponent(str).replace(/[!'()~]|%20|%00/g, function replacer(match) {
    return charMap[match];
  });
}
function AxiosURLSearchParams(params, options) {
  this._pairs = [];
  params && toFormData$1(params, this, options);
}
const prototype = AxiosURLSearchParams.prototype;
prototype.append = function append(name, value) {
  this._pairs.push([name, value]);
};
prototype.toString = function toString2(encoder) {
  const _encode = encoder ? function(value) {
    return encoder.call(this, value, encode$1);
  } : encode$1;
  return this._pairs.map(function each(pair) {
    return _encode(pair[0]) + "=" + _encode(pair[1]);
  }, "").join("&");
};
function encode(val) {
  return encodeURIComponent(val).replace(/%3A/gi, ":").replace(/%24/g, "$").replace(/%2C/gi, ",").replace(/%20/g, "+");
}
function buildURL(url, params, options) {
  if (!params) {
    return url;
  }
  const _encode = options && options.encode || encode;
  if (utils$1.isFunction(options)) {
    options = {
      serialize: options
    };
  }
  const serializeFn = options && options.serialize;
  let serializedParams;
  if (serializeFn) {
    serializedParams = serializeFn(params, options);
  } else {
    serializedParams = utils$1.isURLSearchParams(params) ? params.toString() : new AxiosURLSearchParams(params, options).toString(_encode);
  }
  if (serializedParams) {
    const hashmarkIndex = url.indexOf("#");
    if (hashmarkIndex !== -1) {
      url = url.slice(0, hashmarkIndex);
    }
    url += (url.indexOf("?") === -1 ? "?" : "&") + serializedParams;
  }
  return url;
}
class InterceptorManager {
  constructor() {
    this.handlers = [];
  }
  /**
   * Add a new interceptor to the stack
   *
   * @param {Function} fulfilled The function to handle `then` for a `Promise`
   * @param {Function} rejected The function to handle `reject` for a `Promise`
   *
   * @return {Number} An ID used to remove interceptor later
   */
  use(fulfilled, rejected, options) {
    this.handlers.push({
      fulfilled,
      rejected,
      synchronous: options ? options.synchronous : false,
      runWhen: options ? options.runWhen : null
    });
    return this.handlers.length - 1;
  }
  /**
   * Remove an interceptor from the stack
   *
   * @param {Number} id The ID that was returned by `use`
   *
   * @returns {void}
   */
  eject(id) {
    if (this.handlers[id]) {
      this.handlers[id] = null;
    }
  }
  /**
   * Clear all interceptors from the stack
   *
   * @returns {void}
   */
  clear() {
    if (this.handlers) {
      this.handlers = [];
    }
  }
  /**
   * Iterate over all the registered interceptors
   *
   * This method is particularly useful for skipping over any
   * interceptors that may have become `null` calling `eject`.
   *
   * @param {Function} fn The function to call for each interceptor
   *
   * @returns {void}
   */
  forEach(fn) {
    utils$1.forEach(this.handlers, function forEachHandler(h) {
      if (h !== null) {
        fn(h);
      }
    });
  }
}
const transitionalDefaults = {
  silentJSONParsing: true,
  forcedJSONParsing: true,
  clarifyTimeoutError: false
};
const URLSearchParams$1 = typeof URLSearchParams !== "undefined" ? URLSearchParams : AxiosURLSearchParams;
const FormData$1 = typeof FormData !== "undefined" ? FormData : null;
const Blob$1 = typeof Blob !== "undefined" ? Blob : null;
const platform$1 = {
  isBrowser: true,
  classes: {
    URLSearchParams: URLSearchParams$1,
    FormData: FormData$1,
    Blob: Blob$1
  },
  protocols: ["http", "https", "file", "blob", "url", "data"]
};
const hasBrowserEnv = typeof window !== "undefined" && typeof document !== "undefined";
const _navigator = typeof navigator === "object" && navigator || void 0;
const hasStandardBrowserEnv = hasBrowserEnv && (!_navigator || ["ReactNative", "NativeScript", "NS"].indexOf(_navigator.product) < 0);
const hasStandardBrowserWebWorkerEnv = (() => {
  return typeof WorkerGlobalScope !== "undefined" && // eslint-disable-next-line no-undef
  self instanceof WorkerGlobalScope && typeof self.importScripts === "function";
})();
const origin = hasBrowserEnv && window.location.href || "http://localhost";
const utils = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  hasBrowserEnv,
  hasStandardBrowserEnv,
  hasStandardBrowserWebWorkerEnv,
  navigator: _navigator,
  origin
}, Symbol.toStringTag, { value: "Module" }));
const platform = {
  ...utils,
  ...platform$1
};
function toURLEncodedForm(data, options) {
  return toFormData$1(data, new platform.classes.URLSearchParams(), {
    visitor: function(value, key, path, helpers) {
      if (platform.isNode && utils$1.isBuffer(value)) {
        this.append(key, value.toString("base64"));
        return false;
      }
      return helpers.defaultVisitor.apply(this, arguments);
    },
    ...options
  });
}
function parsePropPath(name) {
  return utils$1.matchAll(/\w+|\[(\w*)]/g, name).map((match) => {
    return match[0] === "[]" ? "" : match[1] || match[0];
  });
}
function arrayToObject(arr) {
  const obj = {};
  const keys = Object.keys(arr);
  let i;
  const len = keys.length;
  let key;
  for (i = 0; i < len; i++) {
    key = keys[i];
    obj[key] = arr[key];
  }
  return obj;
}
function formDataToJSON(formData) {
  function buildPath(path, value, target, index) {
    let name = path[index++];
    if (name === "__proto__") return true;
    const isNumericKey = Number.isFinite(+name);
    const isLast = index >= path.length;
    name = !name && utils$1.isArray(target) ? target.length : name;
    if (isLast) {
      if (utils$1.hasOwnProp(target, name)) {
        target[name] = [target[name], value];
      } else {
        target[name] = value;
      }
      return !isNumericKey;
    }
    if (!target[name] || !utils$1.isObject(target[name])) {
      target[name] = [];
    }
    const result = buildPath(path, value, target[name], index);
    if (result && utils$1.isArray(target[name])) {
      target[name] = arrayToObject(target[name]);
    }
    return !isNumericKey;
  }
  if (utils$1.isFormData(formData) && utils$1.isFunction(formData.entries)) {
    const obj = {};
    utils$1.forEachEntry(formData, (name, value) => {
      buildPath(parsePropPath(name), value, obj, 0);
    });
    return obj;
  }
  return null;
}
function stringifySafely(rawValue, parser, encoder) {
  if (utils$1.isString(rawValue)) {
    try {
      (parser || JSON.parse)(rawValue);
      return utils$1.trim(rawValue);
    } catch (e) {
      if (e.name !== "SyntaxError") {
        throw e;
      }
    }
  }
  return (encoder || JSON.stringify)(rawValue);
}
const defaults = {
  transitional: transitionalDefaults,
  adapter: ["xhr", "http", "fetch"],
  transformRequest: [function transformRequest(data, headers) {
    const contentType = headers.getContentType() || "";
    const hasJSONContentType = contentType.indexOf("application/json") > -1;
    const isObjectPayload = utils$1.isObject(data);
    if (isObjectPayload && utils$1.isHTMLForm(data)) {
      data = new FormData(data);
    }
    const isFormData2 = utils$1.isFormData(data);
    if (isFormData2) {
      return hasJSONContentType ? JSON.stringify(formDataToJSON(data)) : data;
    }
    if (utils$1.isArrayBuffer(data) || utils$1.isBuffer(data) || utils$1.isStream(data) || utils$1.isFile(data) || utils$1.isBlob(data) || utils$1.isReadableStream(data)) {
      return data;
    }
    if (utils$1.isArrayBufferView(data)) {
      return data.buffer;
    }
    if (utils$1.isURLSearchParams(data)) {
      headers.setContentType("application/x-www-form-urlencoded;charset=utf-8", false);
      return data.toString();
    }
    let isFileList2;
    if (isObjectPayload) {
      if (contentType.indexOf("application/x-www-form-urlencoded") > -1) {
        return toURLEncodedForm(data, this.formSerializer).toString();
      }
      if ((isFileList2 = utils$1.isFileList(data)) || contentType.indexOf("multipart/form-data") > -1) {
        const _FormData = this.env && this.env.FormData;
        return toFormData$1(
          isFileList2 ? { "files[]": data } : data,
          _FormData && new _FormData(),
          this.formSerializer
        );
      }
    }
    if (isObjectPayload || hasJSONContentType) {
      headers.setContentType("application/json", false);
      return stringifySafely(data);
    }
    return data;
  }],
  transformResponse: [function transformResponse(data) {
    const transitional2 = this.transitional || defaults.transitional;
    const forcedJSONParsing = transitional2 && transitional2.forcedJSONParsing;
    const JSONRequested = this.responseType === "json";
    if (utils$1.isResponse(data) || utils$1.isReadableStream(data)) {
      return data;
    }
    if (data && utils$1.isString(data) && (forcedJSONParsing && !this.responseType || JSONRequested)) {
      const silentJSONParsing = transitional2 && transitional2.silentJSONParsing;
      const strictJSONParsing = !silentJSONParsing && JSONRequested;
      try {
        return JSON.parse(data, this.parseReviver);
      } catch (e) {
        if (strictJSONParsing) {
          if (e.name === "SyntaxError") {
            throw AxiosError$1.from(e, AxiosError$1.ERR_BAD_RESPONSE, this, null, this.response);
          }
          throw e;
        }
      }
    }
    return data;
  }],
  /**
   * A timeout in milliseconds to abort a request. If set to 0 (default) a
   * timeout is not created.
   */
  timeout: 0,
  xsrfCookieName: "XSRF-TOKEN",
  xsrfHeaderName: "X-XSRF-TOKEN",
  maxContentLength: -1,
  maxBodyLength: -1,
  env: {
    FormData: platform.classes.FormData,
    Blob: platform.classes.Blob
  },
  validateStatus: function validateStatus(status) {
    return status >= 200 && status < 300;
  },
  headers: {
    common: {
      "Accept": "application/json, text/plain, */*",
      "Content-Type": void 0
    }
  }
};
utils$1.forEach(["delete", "get", "head", "post", "put", "patch"], (method) => {
  defaults.headers[method] = {};
});
const ignoreDuplicateOf = utils$1.toObjectSet([
  "age",
  "authorization",
  "content-length",
  "content-type",
  "etag",
  "expires",
  "from",
  "host",
  "if-modified-since",
  "if-unmodified-since",
  "last-modified",
  "location",
  "max-forwards",
  "proxy-authorization",
  "referer",
  "retry-after",
  "user-agent"
]);
const parseHeaders = (rawHeaders) => {
  const parsed = {};
  let key;
  let val;
  let i;
  rawHeaders && rawHeaders.split("\n").forEach(function parser(line) {
    i = line.indexOf(":");
    key = line.substring(0, i).trim().toLowerCase();
    val = line.substring(i + 1).trim();
    if (!key || parsed[key] && ignoreDuplicateOf[key]) {
      return;
    }
    if (key === "set-cookie") {
      if (parsed[key]) {
        parsed[key].push(val);
      } else {
        parsed[key] = [val];
      }
    } else {
      parsed[key] = parsed[key] ? parsed[key] + ", " + val : val;
    }
  });
  return parsed;
};
const $internals = Symbol("internals");
function normalizeHeader(header) {
  return header && String(header).trim().toLowerCase();
}
function normalizeValue(value) {
  if (value === false || value == null) {
    return value;
  }
  return utils$1.isArray(value) ? value.map(normalizeValue) : String(value);
}
function parseTokens(str) {
  const tokens = /* @__PURE__ */ Object.create(null);
  const tokensRE = /([^\s,;=]+)\s*(?:=\s*([^,;]+))?/g;
  let match;
  while (match = tokensRE.exec(str)) {
    tokens[match[1]] = match[2];
  }
  return tokens;
}
const isValidHeaderName = (str) => /^[-_a-zA-Z0-9^`|~,!#$%&'*+.]+$/.test(str.trim());
function matchHeaderValue(context, value, header, filter2, isHeaderNameFilter) {
  if (utils$1.isFunction(filter2)) {
    return filter2.call(this, value, header);
  }
  if (isHeaderNameFilter) {
    value = header;
  }
  if (!utils$1.isString(value)) return;
  if (utils$1.isString(filter2)) {
    return value.indexOf(filter2) !== -1;
  }
  if (utils$1.isRegExp(filter2)) {
    return filter2.test(value);
  }
}
function formatHeader(header) {
  return header.trim().toLowerCase().replace(/([a-z\d])(\w*)/g, (w, char, str) => {
    return char.toUpperCase() + str;
  });
}
function buildAccessors(obj, header) {
  const accessorName = utils$1.toCamelCase(" " + header);
  ["get", "set", "has"].forEach((methodName) => {
    Object.defineProperty(obj, methodName + accessorName, {
      value: function(arg1, arg2, arg3) {
        return this[methodName].call(this, header, arg1, arg2, arg3);
      },
      configurable: true
    });
  });
}
let AxiosHeaders$1 = class AxiosHeaders {
  constructor(headers) {
    headers && this.set(headers);
  }
  set(header, valueOrRewrite, rewrite) {
    const self2 = this;
    function setHeader(_value, _header, _rewrite) {
      const lHeader = normalizeHeader(_header);
      if (!lHeader) {
        throw new Error("header name must be a non-empty string");
      }
      const key = utils$1.findKey(self2, lHeader);
      if (!key || self2[key] === void 0 || _rewrite === true || _rewrite === void 0 && self2[key] !== false) {
        self2[key || _header] = normalizeValue(_value);
      }
    }
    const setHeaders = (headers, _rewrite) => utils$1.forEach(headers, (_value, _header) => setHeader(_value, _header, _rewrite));
    if (utils$1.isPlainObject(header) || header instanceof this.constructor) {
      setHeaders(header, valueOrRewrite);
    } else if (utils$1.isString(header) && (header = header.trim()) && !isValidHeaderName(header)) {
      setHeaders(parseHeaders(header), valueOrRewrite);
    } else if (utils$1.isObject(header) && utils$1.isIterable(header)) {
      let obj = {}, dest, key;
      for (const entry of header) {
        if (!utils$1.isArray(entry)) {
          throw TypeError("Object iterator must return a key-value pair");
        }
        obj[key = entry[0]] = (dest = obj[key]) ? utils$1.isArray(dest) ? [...dest, entry[1]] : [dest, entry[1]] : entry[1];
      }
      setHeaders(obj, valueOrRewrite);
    } else {
      header != null && setHeader(valueOrRewrite, header, rewrite);
    }
    return this;
  }
  get(header, parser) {
    header = normalizeHeader(header);
    if (header) {
      const key = utils$1.findKey(this, header);
      if (key) {
        const value = this[key];
        if (!parser) {
          return value;
        }
        if (parser === true) {
          return parseTokens(value);
        }
        if (utils$1.isFunction(parser)) {
          return parser.call(this, value, key);
        }
        if (utils$1.isRegExp(parser)) {
          return parser.exec(value);
        }
        throw new TypeError("parser must be boolean|regexp|function");
      }
    }
  }
  has(header, matcher) {
    header = normalizeHeader(header);
    if (header) {
      const key = utils$1.findKey(this, header);
      return !!(key && this[key] !== void 0 && (!matcher || matchHeaderValue(this, this[key], key, matcher)));
    }
    return false;
  }
  delete(header, matcher) {
    const self2 = this;
    let deleted = false;
    function deleteHeader(_header) {
      _header = normalizeHeader(_header);
      if (_header) {
        const key = utils$1.findKey(self2, _header);
        if (key && (!matcher || matchHeaderValue(self2, self2[key], key, matcher))) {
          delete self2[key];
          deleted = true;
        }
      }
    }
    if (utils$1.isArray(header)) {
      header.forEach(deleteHeader);
    } else {
      deleteHeader(header);
    }
    return deleted;
  }
  clear(matcher) {
    const keys = Object.keys(this);
    let i = keys.length;
    let deleted = false;
    while (i--) {
      const key = keys[i];
      if (!matcher || matchHeaderValue(this, this[key], key, matcher, true)) {
        delete this[key];
        deleted = true;
      }
    }
    return deleted;
  }
  normalize(format) {
    const self2 = this;
    const headers = {};
    utils$1.forEach(this, (value, header) => {
      const key = utils$1.findKey(headers, header);
      if (key) {
        self2[key] = normalizeValue(value);
        delete self2[header];
        return;
      }
      const normalized = format ? formatHeader(header) : String(header).trim();
      if (normalized !== header) {
        delete self2[header];
      }
      self2[normalized] = normalizeValue(value);
      headers[normalized] = true;
    });
    return this;
  }
  concat(...targets) {
    return this.constructor.concat(this, ...targets);
  }
  toJSON(asStrings) {
    const obj = /* @__PURE__ */ Object.create(null);
    utils$1.forEach(this, (value, header) => {
      value != null && value !== false && (obj[header] = asStrings && utils$1.isArray(value) ? value.join(", ") : value);
    });
    return obj;
  }
  [Symbol.iterator]() {
    return Object.entries(this.toJSON())[Symbol.iterator]();
  }
  toString() {
    return Object.entries(this.toJSON()).map(([header, value]) => header + ": " + value).join("\n");
  }
  getSetCookie() {
    return this.get("set-cookie") || [];
  }
  get [Symbol.toStringTag]() {
    return "AxiosHeaders";
  }
  static from(thing) {
    return thing instanceof this ? thing : new this(thing);
  }
  static concat(first, ...targets) {
    const computed = new this(first);
    targets.forEach((target) => computed.set(target));
    return computed;
  }
  static accessor(header) {
    const internals = this[$internals] = this[$internals] = {
      accessors: {}
    };
    const accessors = internals.accessors;
    const prototype2 = this.prototype;
    function defineAccessor(_header) {
      const lHeader = normalizeHeader(_header);
      if (!accessors[lHeader]) {
        buildAccessors(prototype2, _header);
        accessors[lHeader] = true;
      }
    }
    utils$1.isArray(header) ? header.forEach(defineAccessor) : defineAccessor(header);
    return this;
  }
};
AxiosHeaders$1.accessor(["Content-Type", "Content-Length", "Accept", "Accept-Encoding", "User-Agent", "Authorization"]);
utils$1.reduceDescriptors(AxiosHeaders$1.prototype, ({ value }, key) => {
  let mapped = key[0].toUpperCase() + key.slice(1);
  return {
    get: () => value,
    set(headerValue) {
      this[mapped] = headerValue;
    }
  };
});
utils$1.freezeMethods(AxiosHeaders$1);
function transformData(fns, response) {
  const config = this || defaults;
  const context = response || config;
  const headers = AxiosHeaders$1.from(context.headers);
  let data = context.data;
  utils$1.forEach(fns, function transform(fn) {
    data = fn.call(config, data, headers.normalize(), response ? response.status : void 0);
  });
  headers.normalize();
  return data;
}
function isCancel$1(value) {
  return !!(value && value.__CANCEL__);
}
function CanceledError$1(message, config, request) {
  AxiosError$1.call(this, message == null ? "canceled" : message, AxiosError$1.ERR_CANCELED, config, request);
  this.name = "CanceledError";
}
utils$1.inherits(CanceledError$1, AxiosError$1, {
  __CANCEL__: true
});
function settle(resolve, reject, response) {
  const validateStatus2 = response.config.validateStatus;
  if (!response.status || !validateStatus2 || validateStatus2(response.status)) {
    resolve(response);
  } else {
    reject(new AxiosError$1(
      "Request failed with status code " + response.status,
      [AxiosError$1.ERR_BAD_REQUEST, AxiosError$1.ERR_BAD_RESPONSE][Math.floor(response.status / 100) - 4],
      response.config,
      response.request,
      response
    ));
  }
}
function parseProtocol(url) {
  const match = /^([-+\w]{1,25})(:?\/\/|:)/.exec(url);
  return match && match[1] || "";
}
function speedometer(samplesCount, min) {
  samplesCount = samplesCount || 10;
  const bytes = new Array(samplesCount);
  const timestamps = new Array(samplesCount);
  let head = 0;
  let tail = 0;
  let firstSampleTS;
  min = min !== void 0 ? min : 1e3;
  return function push(chunkLength) {
    const now = Date.now();
    const startedAt = timestamps[tail];
    if (!firstSampleTS) {
      firstSampleTS = now;
    }
    bytes[head] = chunkLength;
    timestamps[head] = now;
    let i = tail;
    let bytesCount = 0;
    while (i !== head) {
      bytesCount += bytes[i++];
      i = i % samplesCount;
    }
    head = (head + 1) % samplesCount;
    if (head === tail) {
      tail = (tail + 1) % samplesCount;
    }
    if (now - firstSampleTS < min) {
      return;
    }
    const passed = startedAt && now - startedAt;
    return passed ? Math.round(bytesCount * 1e3 / passed) : void 0;
  };
}
function throttle(fn, freq) {
  let timestamp = 0;
  let threshold = 1e3 / freq;
  let lastArgs;
  let timer;
  const invoke = (args, now = Date.now()) => {
    timestamp = now;
    lastArgs = null;
    if (timer) {
      clearTimeout(timer);
      timer = null;
    }
    fn(...args);
  };
  const throttled = (...args) => {
    const now = Date.now();
    const passed = now - timestamp;
    if (passed >= threshold) {
      invoke(args, now);
    } else {
      lastArgs = args;
      if (!timer) {
        timer = setTimeout(() => {
          timer = null;
          invoke(lastArgs);
        }, threshold - passed);
      }
    }
  };
  const flush = () => lastArgs && invoke(lastArgs);
  return [throttled, flush];
}
const progressEventReducer = (listener, isDownloadStream, freq = 3) => {
  let bytesNotified = 0;
  const _speedometer = speedometer(50, 250);
  return throttle((e) => {
    const loaded = e.loaded;
    const total = e.lengthComputable ? e.total : void 0;
    const progressBytes = loaded - bytesNotified;
    const rate = _speedometer(progressBytes);
    const inRange = loaded <= total;
    bytesNotified = loaded;
    const data = {
      loaded,
      total,
      progress: total ? loaded / total : void 0,
      bytes: progressBytes,
      rate: rate ? rate : void 0,
      estimated: rate && total && inRange ? (total - loaded) / rate : void 0,
      event: e,
      lengthComputable: total != null,
      [isDownloadStream ? "download" : "upload"]: true
    };
    listener(data);
  }, freq);
};
const progressEventDecorator = (total, throttled) => {
  const lengthComputable = total != null;
  return [(loaded) => throttled[0]({
    lengthComputable,
    total,
    loaded
  }), throttled[1]];
};
const asyncDecorator = (fn) => (...args) => utils$1.asap(() => fn(...args));
const isURLSameOrigin = platform.hasStandardBrowserEnv ? /* @__PURE__ */ ((origin2, isMSIE) => (url) => {
  url = new URL(url, platform.origin);
  return origin2.protocol === url.protocol && origin2.host === url.host && (isMSIE || origin2.port === url.port);
})(
  new URL(platform.origin),
  platform.navigator && /(msie|trident)/i.test(platform.navigator.userAgent)
) : () => true;
const cookies = platform.hasStandardBrowserEnv ? (
  // Standard browser envs support document.cookie
  {
    write(name, value, expires, path, domain, secure, sameSite) {
      if (typeof document === "undefined") return;
      const cookie = [`${name}=${encodeURIComponent(value)}`];
      if (utils$1.isNumber(expires)) {
        cookie.push(`expires=${new Date(expires).toUTCString()}`);
      }
      if (utils$1.isString(path)) {
        cookie.push(`path=${path}`);
      }
      if (utils$1.isString(domain)) {
        cookie.push(`domain=${domain}`);
      }
      if (secure === true) {
        cookie.push("secure");
      }
      if (utils$1.isString(sameSite)) {
        cookie.push(`SameSite=${sameSite}`);
      }
      document.cookie = cookie.join("; ");
    },
    read(name) {
      if (typeof document === "undefined") return null;
      const match = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
      return match ? decodeURIComponent(match[1]) : null;
    },
    remove(name) {
      this.write(name, "", Date.now() - 864e5, "/");
    }
  }
) : (
  // Non-standard browser env (web workers, react-native) lack needed support.
  {
    write() {
    },
    read() {
      return null;
    },
    remove() {
    }
  }
);
function isAbsoluteURL(url) {
  return /^([a-z][a-z\d+\-.]*:)?\/\//i.test(url);
}
function combineURLs(baseURL, relativeURL) {
  return relativeURL ? baseURL.replace(/\/?\/$/, "") + "/" + relativeURL.replace(/^\/+/, "") : baseURL;
}
function buildFullPath(baseURL, requestedURL, allowAbsoluteUrls) {
  let isRelativeUrl = !isAbsoluteURL(requestedURL);
  if (baseURL && (isRelativeUrl || allowAbsoluteUrls == false)) {
    return combineURLs(baseURL, requestedURL);
  }
  return requestedURL;
}
const headersToObject = (thing) => thing instanceof AxiosHeaders$1 ? { ...thing } : thing;
function mergeConfig$1(config1, config2) {
  config2 = config2 || {};
  const config = {};
  function getMergedValue(target, source, prop, caseless) {
    if (utils$1.isPlainObject(target) && utils$1.isPlainObject(source)) {
      return utils$1.merge.call({ caseless }, target, source);
    } else if (utils$1.isPlainObject(source)) {
      return utils$1.merge({}, source);
    } else if (utils$1.isArray(source)) {
      return source.slice();
    }
    return source;
  }
  function mergeDeepProperties(a, b, prop, caseless) {
    if (!utils$1.isUndefined(b)) {
      return getMergedValue(a, b, prop, caseless);
    } else if (!utils$1.isUndefined(a)) {
      return getMergedValue(void 0, a, prop, caseless);
    }
  }
  function valueFromConfig2(a, b) {
    if (!utils$1.isUndefined(b)) {
      return getMergedValue(void 0, b);
    }
  }
  function defaultToConfig2(a, b) {
    if (!utils$1.isUndefined(b)) {
      return getMergedValue(void 0, b);
    } else if (!utils$1.isUndefined(a)) {
      return getMergedValue(void 0, a);
    }
  }
  function mergeDirectKeys(a, b, prop) {
    if (prop in config2) {
      return getMergedValue(a, b);
    } else if (prop in config1) {
      return getMergedValue(void 0, a);
    }
  }
  const mergeMap = {
    url: valueFromConfig2,
    method: valueFromConfig2,
    data: valueFromConfig2,
    baseURL: defaultToConfig2,
    transformRequest: defaultToConfig2,
    transformResponse: defaultToConfig2,
    paramsSerializer: defaultToConfig2,
    timeout: defaultToConfig2,
    timeoutMessage: defaultToConfig2,
    withCredentials: defaultToConfig2,
    withXSRFToken: defaultToConfig2,
    adapter: defaultToConfig2,
    responseType: defaultToConfig2,
    xsrfCookieName: defaultToConfig2,
    xsrfHeaderName: defaultToConfig2,
    onUploadProgress: defaultToConfig2,
    onDownloadProgress: defaultToConfig2,
    decompress: defaultToConfig2,
    maxContentLength: defaultToConfig2,
    maxBodyLength: defaultToConfig2,
    beforeRedirect: defaultToConfig2,
    transport: defaultToConfig2,
    httpAgent: defaultToConfig2,
    httpsAgent: defaultToConfig2,
    cancelToken: defaultToConfig2,
    socketPath: defaultToConfig2,
    responseEncoding: defaultToConfig2,
    validateStatus: mergeDirectKeys,
    headers: (a, b, prop) => mergeDeepProperties(headersToObject(a), headersToObject(b), prop, true)
  };
  utils$1.forEach(Object.keys({ ...config1, ...config2 }), function computeConfigValue(prop) {
    const merge2 = mergeMap[prop] || mergeDeepProperties;
    const configValue = merge2(config1[prop], config2[prop], prop);
    utils$1.isUndefined(configValue) && merge2 !== mergeDirectKeys || (config[prop] = configValue);
  });
  return config;
}
const resolveConfig = (config) => {
  const newConfig = mergeConfig$1({}, config);
  let { data, withXSRFToken, xsrfHeaderName, xsrfCookieName, headers, auth } = newConfig;
  newConfig.headers = headers = AxiosHeaders$1.from(headers);
  newConfig.url = buildURL(buildFullPath(newConfig.baseURL, newConfig.url, newConfig.allowAbsoluteUrls), config.params, config.paramsSerializer);
  if (auth) {
    headers.set(
      "Authorization",
      "Basic " + btoa((auth.username || "") + ":" + (auth.password ? unescape(encodeURIComponent(auth.password)) : ""))
    );
  }
  if (utils$1.isFormData(data)) {
    if (platform.hasStandardBrowserEnv || platform.hasStandardBrowserWebWorkerEnv) {
      headers.setContentType(void 0);
    } else if (utils$1.isFunction(data.getHeaders)) {
      const formHeaders = data.getHeaders();
      const allowedHeaders = ["content-type", "content-length"];
      Object.entries(formHeaders).forEach(([key, val]) => {
        if (allowedHeaders.includes(key.toLowerCase())) {
          headers.set(key, val);
        }
      });
    }
  }
  if (platform.hasStandardBrowserEnv) {
    withXSRFToken && utils$1.isFunction(withXSRFToken) && (withXSRFToken = withXSRFToken(newConfig));
    if (withXSRFToken || withXSRFToken !== false && isURLSameOrigin(newConfig.url)) {
      const xsrfValue = xsrfHeaderName && xsrfCookieName && cookies.read(xsrfCookieName);
      if (xsrfValue) {
        headers.set(xsrfHeaderName, xsrfValue);
      }
    }
  }
  return newConfig;
};
const isXHRAdapterSupported = typeof XMLHttpRequest !== "undefined";
const xhrAdapter = isXHRAdapterSupported && function(config) {
  return new Promise(function dispatchXhrRequest(resolve, reject) {
    const _config = resolveConfig(config);
    let requestData = _config.data;
    const requestHeaders = AxiosHeaders$1.from(_config.headers).normalize();
    let { responseType, onUploadProgress, onDownloadProgress } = _config;
    let onCanceled;
    let uploadThrottled, downloadThrottled;
    let flushUpload, flushDownload;
    function done() {
      flushUpload && flushUpload();
      flushDownload && flushDownload();
      _config.cancelToken && _config.cancelToken.unsubscribe(onCanceled);
      _config.signal && _config.signal.removeEventListener("abort", onCanceled);
    }
    let request = new XMLHttpRequest();
    request.open(_config.method.toUpperCase(), _config.url, true);
    request.timeout = _config.timeout;
    function onloadend() {
      if (!request) {
        return;
      }
      const responseHeaders = AxiosHeaders$1.from(
        "getAllResponseHeaders" in request && request.getAllResponseHeaders()
      );
      const responseData = !responseType || responseType === "text" || responseType === "json" ? request.responseText : request.response;
      const response = {
        data: responseData,
        status: request.status,
        statusText: request.statusText,
        headers: responseHeaders,
        config,
        request
      };
      settle(function _resolve(value) {
        resolve(value);
        done();
      }, function _reject(err) {
        reject(err);
        done();
      }, response);
      request = null;
    }
    if ("onloadend" in request) {
      request.onloadend = onloadend;
    } else {
      request.onreadystatechange = function handleLoad() {
        if (!request || request.readyState !== 4) {
          return;
        }
        if (request.status === 0 && !(request.responseURL && request.responseURL.indexOf("file:") === 0)) {
          return;
        }
        setTimeout(onloadend);
      };
    }
    request.onabort = function handleAbort() {
      if (!request) {
        return;
      }
      reject(new AxiosError$1("Request aborted", AxiosError$1.ECONNABORTED, config, request));
      request = null;
    };
    request.onerror = function handleError(event) {
      const msg = event && event.message ? event.message : "Network Error";
      const err = new AxiosError$1(msg, AxiosError$1.ERR_NETWORK, config, request);
      err.event = event || null;
      reject(err);
      request = null;
    };
    request.ontimeout = function handleTimeout() {
      let timeoutErrorMessage = _config.timeout ? "timeout of " + _config.timeout + "ms exceeded" : "timeout exceeded";
      const transitional2 = _config.transitional || transitionalDefaults;
      if (_config.timeoutErrorMessage) {
        timeoutErrorMessage = _config.timeoutErrorMessage;
      }
      reject(new AxiosError$1(
        timeoutErrorMessage,
        transitional2.clarifyTimeoutError ? AxiosError$1.ETIMEDOUT : AxiosError$1.ECONNABORTED,
        config,
        request
      ));
      request = null;
    };
    requestData === void 0 && requestHeaders.setContentType(null);
    if ("setRequestHeader" in request) {
      utils$1.forEach(requestHeaders.toJSON(), function setRequestHeader(val, key) {
        request.setRequestHeader(key, val);
      });
    }
    if (!utils$1.isUndefined(_config.withCredentials)) {
      request.withCredentials = !!_config.withCredentials;
    }
    if (responseType && responseType !== "json") {
      request.responseType = _config.responseType;
    }
    if (onDownloadProgress) {
      [downloadThrottled, flushDownload] = progressEventReducer(onDownloadProgress, true);
      request.addEventListener("progress", downloadThrottled);
    }
    if (onUploadProgress && request.upload) {
      [uploadThrottled, flushUpload] = progressEventReducer(onUploadProgress);
      request.upload.addEventListener("progress", uploadThrottled);
      request.upload.addEventListener("loadend", flushUpload);
    }
    if (_config.cancelToken || _config.signal) {
      onCanceled = (cancel) => {
        if (!request) {
          return;
        }
        reject(!cancel || cancel.type ? new CanceledError$1(null, config, request) : cancel);
        request.abort();
        request = null;
      };
      _config.cancelToken && _config.cancelToken.subscribe(onCanceled);
      if (_config.signal) {
        _config.signal.aborted ? onCanceled() : _config.signal.addEventListener("abort", onCanceled);
      }
    }
    const protocol = parseProtocol(_config.url);
    if (protocol && platform.protocols.indexOf(protocol) === -1) {
      reject(new AxiosError$1("Unsupported protocol " + protocol + ":", AxiosError$1.ERR_BAD_REQUEST, config));
      return;
    }
    request.send(requestData || null);
  });
};
const composeSignals = (signals, timeout) => {
  const { length } = signals = signals ? signals.filter(Boolean) : [];
  if (timeout || length) {
    let controller = new AbortController();
    let aborted;
    const onabort = function(reason) {
      if (!aborted) {
        aborted = true;
        unsubscribe();
        const err = reason instanceof Error ? reason : this.reason;
        controller.abort(err instanceof AxiosError$1 ? err : new CanceledError$1(err instanceof Error ? err.message : err));
      }
    };
    let timer = timeout && setTimeout(() => {
      timer = null;
      onabort(new AxiosError$1(`timeout ${timeout} of ms exceeded`, AxiosError$1.ETIMEDOUT));
    }, timeout);
    const unsubscribe = () => {
      if (signals) {
        timer && clearTimeout(timer);
        timer = null;
        signals.forEach((signal2) => {
          signal2.unsubscribe ? signal2.unsubscribe(onabort) : signal2.removeEventListener("abort", onabort);
        });
        signals = null;
      }
    };
    signals.forEach((signal2) => signal2.addEventListener("abort", onabort));
    const { signal } = controller;
    signal.unsubscribe = () => utils$1.asap(unsubscribe);
    return signal;
  }
};
const streamChunk = function* (chunk, chunkSize) {
  let len = chunk.byteLength;
  if (len < chunkSize) {
    yield chunk;
    return;
  }
  let pos = 0;
  let end;
  while (pos < len) {
    end = pos + chunkSize;
    yield chunk.slice(pos, end);
    pos = end;
  }
};
const readBytes = async function* (iterable, chunkSize) {
  for await (const chunk of readStream(iterable)) {
    yield* streamChunk(chunk, chunkSize);
  }
};
const readStream = async function* (stream) {
  if (stream[Symbol.asyncIterator]) {
    yield* stream;
    return;
  }
  const reader = stream.getReader();
  try {
    for (; ; ) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      yield value;
    }
  } finally {
    await reader.cancel();
  }
};
const trackStream = (stream, chunkSize, onProgress, onFinish) => {
  const iterator2 = readBytes(stream, chunkSize);
  let bytes = 0;
  let done;
  let _onFinish = (e) => {
    if (!done) {
      done = true;
      onFinish && onFinish(e);
    }
  };
  return new ReadableStream({
    async pull(controller) {
      try {
        const { done: done2, value } = await iterator2.next();
        if (done2) {
          _onFinish();
          controller.close();
          return;
        }
        let len = value.byteLength;
        if (onProgress) {
          let loadedBytes = bytes += len;
          onProgress(loadedBytes);
        }
        controller.enqueue(new Uint8Array(value));
      } catch (err) {
        _onFinish(err);
        throw err;
      }
    },
    cancel(reason) {
      _onFinish(reason);
      return iterator2.return();
    }
  }, {
    highWaterMark: 2
  });
};
const DEFAULT_CHUNK_SIZE = 64 * 1024;
const { isFunction } = utils$1;
const globalFetchAPI = (({ Request, Response }) => ({
  Request,
  Response
}))(utils$1.global);
const {
  ReadableStream: ReadableStream$1,
  TextEncoder
} = utils$1.global;
const test = (fn, ...args) => {
  try {
    return !!fn(...args);
  } catch (e) {
    return false;
  }
};
const factory = (env) => {
  env = utils$1.merge.call({
    skipUndefined: true
  }, globalFetchAPI, env);
  const { fetch: envFetch, Request, Response } = env;
  const isFetchSupported = envFetch ? isFunction(envFetch) : typeof fetch === "function";
  const isRequestSupported = isFunction(Request);
  const isResponseSupported = isFunction(Response);
  if (!isFetchSupported) {
    return false;
  }
  const isReadableStreamSupported = isFetchSupported && isFunction(ReadableStream$1);
  const encodeText = isFetchSupported && (typeof TextEncoder === "function" ? /* @__PURE__ */ ((encoder) => (str) => encoder.encode(str))(new TextEncoder()) : async (str) => new Uint8Array(await new Request(str).arrayBuffer()));
  const supportsRequestStream = isRequestSupported && isReadableStreamSupported && test(() => {
    let duplexAccessed = false;
    const hasContentType = new Request(platform.origin, {
      body: new ReadableStream$1(),
      method: "POST",
      get duplex() {
        duplexAccessed = true;
        return "half";
      }
    }).headers.has("Content-Type");
    return duplexAccessed && !hasContentType;
  });
  const supportsResponseStream = isResponseSupported && isReadableStreamSupported && test(() => utils$1.isReadableStream(new Response("").body));
  const resolvers = {
    stream: supportsResponseStream && ((res) => res.body)
  };
  isFetchSupported && (() => {
    ["text", "arrayBuffer", "blob", "formData", "stream"].forEach((type) => {
      !resolvers[type] && (resolvers[type] = (res, config) => {
        let method = res && res[type];
        if (method) {
          return method.call(res);
        }
        throw new AxiosError$1(`Response type '${type}' is not supported`, AxiosError$1.ERR_NOT_SUPPORT, config);
      });
    });
  })();
  const getBodyLength = async (body) => {
    if (body == null) {
      return 0;
    }
    if (utils$1.isBlob(body)) {
      return body.size;
    }
    if (utils$1.isSpecCompliantForm(body)) {
      const _request = new Request(platform.origin, {
        method: "POST",
        body
      });
      return (await _request.arrayBuffer()).byteLength;
    }
    if (utils$1.isArrayBufferView(body) || utils$1.isArrayBuffer(body)) {
      return body.byteLength;
    }
    if (utils$1.isURLSearchParams(body)) {
      body = body + "";
    }
    if (utils$1.isString(body)) {
      return (await encodeText(body)).byteLength;
    }
  };
  const resolveBodyLength = async (headers, body) => {
    const length = utils$1.toFiniteNumber(headers.getContentLength());
    return length == null ? getBodyLength(body) : length;
  };
  return async (config) => {
    let {
      url,
      method,
      data,
      signal,
      cancelToken,
      timeout,
      onDownloadProgress,
      onUploadProgress,
      responseType,
      headers,
      withCredentials = "same-origin",
      fetchOptions
    } = resolveConfig(config);
    let _fetch = envFetch || fetch;
    responseType = responseType ? (responseType + "").toLowerCase() : "text";
    let composedSignal = composeSignals([signal, cancelToken && cancelToken.toAbortSignal()], timeout);
    let request = null;
    const unsubscribe = composedSignal && composedSignal.unsubscribe && (() => {
      composedSignal.unsubscribe();
    });
    let requestContentLength;
    try {
      if (onUploadProgress && supportsRequestStream && method !== "get" && method !== "head" && (requestContentLength = await resolveBodyLength(headers, data)) !== 0) {
        let _request = new Request(url, {
          method: "POST",
          body: data,
          duplex: "half"
        });
        let contentTypeHeader;
        if (utils$1.isFormData(data) && (contentTypeHeader = _request.headers.get("content-type"))) {
          headers.setContentType(contentTypeHeader);
        }
        if (_request.body) {
          const [onProgress, flush] = progressEventDecorator(
            requestContentLength,
            progressEventReducer(asyncDecorator(onUploadProgress))
          );
          data = trackStream(_request.body, DEFAULT_CHUNK_SIZE, onProgress, flush);
        }
      }
      if (!utils$1.isString(withCredentials)) {
        withCredentials = withCredentials ? "include" : "omit";
      }
      const isCredentialsSupported = isRequestSupported && "credentials" in Request.prototype;
      const resolvedOptions = {
        ...fetchOptions,
        signal: composedSignal,
        method: method.toUpperCase(),
        headers: headers.normalize().toJSON(),
        body: data,
        duplex: "half",
        credentials: isCredentialsSupported ? withCredentials : void 0
      };
      request = isRequestSupported && new Request(url, resolvedOptions);
      let response = await (isRequestSupported ? _fetch(request, fetchOptions) : _fetch(url, resolvedOptions));
      const isStreamResponse = supportsResponseStream && (responseType === "stream" || responseType === "response");
      if (supportsResponseStream && (onDownloadProgress || isStreamResponse && unsubscribe)) {
        const options = {};
        ["status", "statusText", "headers"].forEach((prop) => {
          options[prop] = response[prop];
        });
        const responseContentLength = utils$1.toFiniteNumber(response.headers.get("content-length"));
        const [onProgress, flush] = onDownloadProgress && progressEventDecorator(
          responseContentLength,
          progressEventReducer(asyncDecorator(onDownloadProgress), true)
        ) || [];
        response = new Response(
          trackStream(response.body, DEFAULT_CHUNK_SIZE, onProgress, () => {
            flush && flush();
            unsubscribe && unsubscribe();
          }),
          options
        );
      }
      responseType = responseType || "text";
      let responseData = await resolvers[utils$1.findKey(resolvers, responseType) || "text"](response, config);
      !isStreamResponse && unsubscribe && unsubscribe();
      return await new Promise((resolve, reject) => {
        settle(resolve, reject, {
          data: responseData,
          headers: AxiosHeaders$1.from(response.headers),
          status: response.status,
          statusText: response.statusText,
          config,
          request
        });
      });
    } catch (err) {
      unsubscribe && unsubscribe();
      if (err && err.name === "TypeError" && /Load failed|fetch/i.test(err.message)) {
        throw Object.assign(
          new AxiosError$1("Network Error", AxiosError$1.ERR_NETWORK, config, request),
          {
            cause: err.cause || err
          }
        );
      }
      throw AxiosError$1.from(err, err && err.code, config, request);
    }
  };
};
const seedCache = /* @__PURE__ */ new Map();
const getFetch = (config) => {
  let env = config && config.env || {};
  const { fetch: fetch2, Request, Response } = env;
  const seeds = [
    Request,
    Response,
    fetch2
  ];
  let len = seeds.length, i = len, seed, target, map = seedCache;
  while (i--) {
    seed = seeds[i];
    target = map.get(seed);
    target === void 0 && map.set(seed, target = i ? /* @__PURE__ */ new Map() : factory(env));
    map = target;
  }
  return target;
};
getFetch();
const knownAdapters = {
  http: httpAdapter,
  xhr: xhrAdapter,
  fetch: {
    get: getFetch
  }
};
utils$1.forEach(knownAdapters, (fn, value) => {
  if (fn) {
    try {
      Object.defineProperty(fn, "name", { value });
    } catch (e) {
    }
    Object.defineProperty(fn, "adapterName", { value });
  }
});
const renderReason = (reason) => `- ${reason}`;
const isResolvedHandle = (adapter) => utils$1.isFunction(adapter) || adapter === null || adapter === false;
function getAdapter$1(adapters2, config) {
  adapters2 = utils$1.isArray(adapters2) ? adapters2 : [adapters2];
  const { length } = adapters2;
  let nameOrAdapter;
  let adapter;
  const rejectedReasons = {};
  for (let i = 0; i < length; i++) {
    nameOrAdapter = adapters2[i];
    let id;
    adapter = nameOrAdapter;
    if (!isResolvedHandle(nameOrAdapter)) {
      adapter = knownAdapters[(id = String(nameOrAdapter)).toLowerCase()];
      if (adapter === void 0) {
        throw new AxiosError$1(`Unknown adapter '${id}'`);
      }
    }
    if (adapter && (utils$1.isFunction(adapter) || (adapter = adapter.get(config)))) {
      break;
    }
    rejectedReasons[id || "#" + i] = adapter;
  }
  if (!adapter) {
    const reasons = Object.entries(rejectedReasons).map(
      ([id, state]) => `adapter ${id} ` + (state === false ? "is not supported by the environment" : "is not available in the build")
    );
    let s = length ? reasons.length > 1 ? "since :\n" + reasons.map(renderReason).join("\n") : " " + renderReason(reasons[0]) : "as no adapter specified";
    throw new AxiosError$1(
      `There is no suitable adapter to dispatch the request ` + s,
      "ERR_NOT_SUPPORT"
    );
  }
  return adapter;
}
const adapters = {
  /**
   * Resolve an adapter from a list of adapter names or functions.
   * @type {Function}
   */
  getAdapter: getAdapter$1,
  /**
   * Exposes all known adapters
   * @type {Object<string, Function|Object>}
   */
  adapters: knownAdapters
};
function throwIfCancellationRequested(config) {
  if (config.cancelToken) {
    config.cancelToken.throwIfRequested();
  }
  if (config.signal && config.signal.aborted) {
    throw new CanceledError$1(null, config);
  }
}
function dispatchRequest(config) {
  throwIfCancellationRequested(config);
  config.headers = AxiosHeaders$1.from(config.headers);
  config.data = transformData.call(
    config,
    config.transformRequest
  );
  if (["post", "put", "patch"].indexOf(config.method) !== -1) {
    config.headers.setContentType("application/x-www-form-urlencoded", false);
  }
  const adapter = adapters.getAdapter(config.adapter || defaults.adapter, config);
  return adapter(config).then(function onAdapterResolution(response) {
    throwIfCancellationRequested(config);
    response.data = transformData.call(
      config,
      config.transformResponse,
      response
    );
    response.headers = AxiosHeaders$1.from(response.headers);
    return response;
  }, function onAdapterRejection(reason) {
    if (!isCancel$1(reason)) {
      throwIfCancellationRequested(config);
      if (reason && reason.response) {
        reason.response.data = transformData.call(
          config,
          config.transformResponse,
          reason.response
        );
        reason.response.headers = AxiosHeaders$1.from(reason.response.headers);
      }
    }
    return Promise.reject(reason);
  });
}
const VERSION$1 = "1.13.2";
const validators$1 = {};
["object", "boolean", "number", "function", "string", "symbol"].forEach((type, i) => {
  validators$1[type] = function validator2(thing) {
    return typeof thing === type || "a" + (i < 1 ? "n " : " ") + type;
  };
});
const deprecatedWarnings = {};
validators$1.transitional = function transitional(validator2, version, message) {
  function formatMessage(opt, desc) {
    return "[Axios v" + VERSION$1 + "] Transitional option '" + opt + "'" + desc + (message ? ". " + message : "");
  }
  return (value, opt, opts) => {
    if (validator2 === false) {
      throw new AxiosError$1(
        formatMessage(opt, " has been removed" + (version ? " in " + version : "")),
        AxiosError$1.ERR_DEPRECATED
      );
    }
    if (version && !deprecatedWarnings[opt]) {
      deprecatedWarnings[opt] = true;
      console.warn(
        formatMessage(
          opt,
          " has been deprecated since v" + version + " and will be removed in the near future"
        )
      );
    }
    return validator2 ? validator2(value, opt, opts) : true;
  };
};
validators$1.spelling = function spelling(correctSpelling) {
  return (value, opt) => {
    console.warn(`${opt} is likely a misspelling of ${correctSpelling}`);
    return true;
  };
};
function assertOptions(options, schema, allowUnknown) {
  if (typeof options !== "object") {
    throw new AxiosError$1("options must be an object", AxiosError$1.ERR_BAD_OPTION_VALUE);
  }
  const keys = Object.keys(options);
  let i = keys.length;
  while (i-- > 0) {
    const opt = keys[i];
    const validator2 = schema[opt];
    if (validator2) {
      const value = options[opt];
      const result = value === void 0 || validator2(value, opt, options);
      if (result !== true) {
        throw new AxiosError$1("option " + opt + " must be " + result, AxiosError$1.ERR_BAD_OPTION_VALUE);
      }
      continue;
    }
    if (allowUnknown !== true) {
      throw new AxiosError$1("Unknown option " + opt, AxiosError$1.ERR_BAD_OPTION);
    }
  }
}
const validator = {
  assertOptions,
  validators: validators$1
};
const validators = validator.validators;
let Axios$1 = class Axios {
  constructor(instanceConfig) {
    this.defaults = instanceConfig || {};
    this.interceptors = {
      request: new InterceptorManager(),
      response: new InterceptorManager()
    };
  }
  /**
   * Dispatch a request
   *
   * @param {String|Object} configOrUrl The config specific for this request (merged with this.defaults)
   * @param {?Object} config
   *
   * @returns {Promise} The Promise to be fulfilled
   */
  async request(configOrUrl, config) {
    try {
      return await this._request(configOrUrl, config);
    } catch (err) {
      if (err instanceof Error) {
        let dummy = {};
        Error.captureStackTrace ? Error.captureStackTrace(dummy) : dummy = new Error();
        const stack = dummy.stack ? dummy.stack.replace(/^.+\n/, "") : "";
        try {
          if (!err.stack) {
            err.stack = stack;
          } else if (stack && !String(err.stack).endsWith(stack.replace(/^.+\n.+\n/, ""))) {
            err.stack += "\n" + stack;
          }
        } catch (e) {
        }
      }
      throw err;
    }
  }
  _request(configOrUrl, config) {
    if (typeof configOrUrl === "string") {
      config = config || {};
      config.url = configOrUrl;
    } else {
      config = configOrUrl || {};
    }
    config = mergeConfig$1(this.defaults, config);
    const { transitional: transitional2, paramsSerializer, headers } = config;
    if (transitional2 !== void 0) {
      validator.assertOptions(transitional2, {
        silentJSONParsing: validators.transitional(validators.boolean),
        forcedJSONParsing: validators.transitional(validators.boolean),
        clarifyTimeoutError: validators.transitional(validators.boolean)
      }, false);
    }
    if (paramsSerializer != null) {
      if (utils$1.isFunction(paramsSerializer)) {
        config.paramsSerializer = {
          serialize: paramsSerializer
        };
      } else {
        validator.assertOptions(paramsSerializer, {
          encode: validators.function,
          serialize: validators.function
        }, true);
      }
    }
    if (config.allowAbsoluteUrls !== void 0) ;
    else if (this.defaults.allowAbsoluteUrls !== void 0) {
      config.allowAbsoluteUrls = this.defaults.allowAbsoluteUrls;
    } else {
      config.allowAbsoluteUrls = true;
    }
    validator.assertOptions(config, {
      baseUrl: validators.spelling("baseURL"),
      withXsrfToken: validators.spelling("withXSRFToken")
    }, true);
    config.method = (config.method || this.defaults.method || "get").toLowerCase();
    let contextHeaders = headers && utils$1.merge(
      headers.common,
      headers[config.method]
    );
    headers && utils$1.forEach(
      ["delete", "get", "head", "post", "put", "patch", "common"],
      (method) => {
        delete headers[method];
      }
    );
    config.headers = AxiosHeaders$1.concat(contextHeaders, headers);
    const requestInterceptorChain = [];
    let synchronousRequestInterceptors = true;
    this.interceptors.request.forEach(function unshiftRequestInterceptors(interceptor) {
      if (typeof interceptor.runWhen === "function" && interceptor.runWhen(config) === false) {
        return;
      }
      synchronousRequestInterceptors = synchronousRequestInterceptors && interceptor.synchronous;
      requestInterceptorChain.unshift(interceptor.fulfilled, interceptor.rejected);
    });
    const responseInterceptorChain = [];
    this.interceptors.response.forEach(function pushResponseInterceptors(interceptor) {
      responseInterceptorChain.push(interceptor.fulfilled, interceptor.rejected);
    });
    let promise;
    let i = 0;
    let len;
    if (!synchronousRequestInterceptors) {
      const chain = [dispatchRequest.bind(this), void 0];
      chain.unshift(...requestInterceptorChain);
      chain.push(...responseInterceptorChain);
      len = chain.length;
      promise = Promise.resolve(config);
      while (i < len) {
        promise = promise.then(chain[i++], chain[i++]);
      }
      return promise;
    }
    len = requestInterceptorChain.length;
    let newConfig = config;
    while (i < len) {
      const onFulfilled = requestInterceptorChain[i++];
      const onRejected = requestInterceptorChain[i++];
      try {
        newConfig = onFulfilled(newConfig);
      } catch (error) {
        onRejected.call(this, error);
        break;
      }
    }
    try {
      promise = dispatchRequest.call(this, newConfig);
    } catch (error) {
      return Promise.reject(error);
    }
    i = 0;
    len = responseInterceptorChain.length;
    while (i < len) {
      promise = promise.then(responseInterceptorChain[i++], responseInterceptorChain[i++]);
    }
    return promise;
  }
  getUri(config) {
    config = mergeConfig$1(this.defaults, config);
    const fullPath = buildFullPath(config.baseURL, config.url, config.allowAbsoluteUrls);
    return buildURL(fullPath, config.params, config.paramsSerializer);
  }
};
utils$1.forEach(["delete", "get", "head", "options"], function forEachMethodNoData(method) {
  Axios$1.prototype[method] = function(url, config) {
    return this.request(mergeConfig$1(config || {}, {
      method,
      url,
      data: (config || {}).data
    }));
  };
});
utils$1.forEach(["post", "put", "patch"], function forEachMethodWithData(method) {
  function generateHTTPMethod(isForm) {
    return function httpMethod(url, data, config) {
      return this.request(mergeConfig$1(config || {}, {
        method,
        headers: isForm ? {
          "Content-Type": "multipart/form-data"
        } : {},
        url,
        data
      }));
    };
  }
  Axios$1.prototype[method] = generateHTTPMethod();
  Axios$1.prototype[method + "Form"] = generateHTTPMethod(true);
});
let CancelToken$1 = class CancelToken {
  constructor(executor) {
    if (typeof executor !== "function") {
      throw new TypeError("executor must be a function.");
    }
    let resolvePromise;
    this.promise = new Promise(function promiseExecutor(resolve) {
      resolvePromise = resolve;
    });
    const token = this;
    this.promise.then((cancel) => {
      if (!token._listeners) return;
      let i = token._listeners.length;
      while (i-- > 0) {
        token._listeners[i](cancel);
      }
      token._listeners = null;
    });
    this.promise.then = (onfulfilled) => {
      let _resolve;
      const promise = new Promise((resolve) => {
        token.subscribe(resolve);
        _resolve = resolve;
      }).then(onfulfilled);
      promise.cancel = function reject() {
        token.unsubscribe(_resolve);
      };
      return promise;
    };
    executor(function cancel(message, config, request) {
      if (token.reason) {
        return;
      }
      token.reason = new CanceledError$1(message, config, request);
      resolvePromise(token.reason);
    });
  }
  /**
   * Throws a `CanceledError` if cancellation has been requested.
   */
  throwIfRequested() {
    if (this.reason) {
      throw this.reason;
    }
  }
  /**
   * Subscribe to the cancel signal
   */
  subscribe(listener) {
    if (this.reason) {
      listener(this.reason);
      return;
    }
    if (this._listeners) {
      this._listeners.push(listener);
    } else {
      this._listeners = [listener];
    }
  }
  /**
   * Unsubscribe from the cancel signal
   */
  unsubscribe(listener) {
    if (!this._listeners) {
      return;
    }
    const index = this._listeners.indexOf(listener);
    if (index !== -1) {
      this._listeners.splice(index, 1);
    }
  }
  toAbortSignal() {
    const controller = new AbortController();
    const abort = (err) => {
      controller.abort(err);
    };
    this.subscribe(abort);
    controller.signal.unsubscribe = () => this.unsubscribe(abort);
    return controller.signal;
  }
  /**
   * Returns an object that contains a new `CancelToken` and a function that, when called,
   * cancels the `CancelToken`.
   */
  static source() {
    let cancel;
    const token = new CancelToken(function executor(c) {
      cancel = c;
    });
    return {
      token,
      cancel
    };
  }
};
function spread$1(callback) {
  return function wrap(arr) {
    return callback.apply(null, arr);
  };
}
function isAxiosError$1(payload) {
  return utils$1.isObject(payload) && payload.isAxiosError === true;
}
const HttpStatusCode$1 = {
  Continue: 100,
  SwitchingProtocols: 101,
  Processing: 102,
  EarlyHints: 103,
  Ok: 200,
  Created: 201,
  Accepted: 202,
  NonAuthoritativeInformation: 203,
  NoContent: 204,
  ResetContent: 205,
  PartialContent: 206,
  MultiStatus: 207,
  AlreadyReported: 208,
  ImUsed: 226,
  MultipleChoices: 300,
  MovedPermanently: 301,
  Found: 302,
  SeeOther: 303,
  NotModified: 304,
  UseProxy: 305,
  Unused: 306,
  TemporaryRedirect: 307,
  PermanentRedirect: 308,
  BadRequest: 400,
  Unauthorized: 401,
  PaymentRequired: 402,
  Forbidden: 403,
  NotFound: 404,
  MethodNotAllowed: 405,
  NotAcceptable: 406,
  ProxyAuthenticationRequired: 407,
  RequestTimeout: 408,
  Conflict: 409,
  Gone: 410,
  LengthRequired: 411,
  PreconditionFailed: 412,
  PayloadTooLarge: 413,
  UriTooLong: 414,
  UnsupportedMediaType: 415,
  RangeNotSatisfiable: 416,
  ExpectationFailed: 417,
  ImATeapot: 418,
  MisdirectedRequest: 421,
  UnprocessableEntity: 422,
  Locked: 423,
  FailedDependency: 424,
  TooEarly: 425,
  UpgradeRequired: 426,
  PreconditionRequired: 428,
  TooManyRequests: 429,
  RequestHeaderFieldsTooLarge: 431,
  UnavailableForLegalReasons: 451,
  InternalServerError: 500,
  NotImplemented: 501,
  BadGateway: 502,
  ServiceUnavailable: 503,
  GatewayTimeout: 504,
  HttpVersionNotSupported: 505,
  VariantAlsoNegotiates: 506,
  InsufficientStorage: 507,
  LoopDetected: 508,
  NotExtended: 510,
  NetworkAuthenticationRequired: 511,
  WebServerIsDown: 521,
  ConnectionTimedOut: 522,
  OriginIsUnreachable: 523,
  TimeoutOccurred: 524,
  SslHandshakeFailed: 525,
  InvalidSslCertificate: 526
};
Object.entries(HttpStatusCode$1).forEach(([key, value]) => {
  HttpStatusCode$1[value] = key;
});
function createInstance(defaultConfig) {
  const context = new Axios$1(defaultConfig);
  const instance = bind(Axios$1.prototype.request, context);
  utils$1.extend(instance, Axios$1.prototype, context, { allOwnKeys: true });
  utils$1.extend(instance, context, null, { allOwnKeys: true });
  instance.create = function create2(instanceConfig) {
    return createInstance(mergeConfig$1(defaultConfig, instanceConfig));
  };
  return instance;
}
const axios = createInstance(defaults);
axios.Axios = Axios$1;
axios.CanceledError = CanceledError$1;
axios.CancelToken = CancelToken$1;
axios.isCancel = isCancel$1;
axios.VERSION = VERSION$1;
axios.toFormData = toFormData$1;
axios.AxiosError = AxiosError$1;
axios.Cancel = axios.CanceledError;
axios.all = function all(promises) {
  return Promise.all(promises);
};
axios.spread = spread$1;
axios.isAxiosError = isAxiosError$1;
axios.mergeConfig = mergeConfig$1;
axios.AxiosHeaders = AxiosHeaders$1;
axios.formToJSON = (thing) => formDataToJSON(utils$1.isHTMLForm(thing) ? new FormData(thing) : thing);
axios.getAdapter = adapters.getAdapter;
axios.HttpStatusCode = HttpStatusCode$1;
axios.default = axios;
const {
  Axios: Axios2,
  AxiosError,
  CanceledError,
  isCancel,
  CancelToken: CancelToken2,
  VERSION,
  all: all2,
  Cancel,
  isAxiosError,
  spread,
  toFormData,
  AxiosHeaders: AxiosHeaders2,
  HttpStatusCode,
  formToJSON,
  getAdapter,
  mergeConfig
} = axios;
const getBaseUrl = () => {
  if (typeof window !== "undefined" && window.location.pathname.startsWith("/ui")) {
    return "/api";
  }
  return "/api";
};
const apiClient = axios.create({
  baseURL: getBaseUrl(),
  timeout: 3e4,
  headers: {
    "Content-Type": "application/json"
  }
});
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    var _a, _b;
    const status = (_a = error.response) == null ? void 0 : _a.status;
    const responseData = (_b = error.response) == null ? void 0 : _b.data;
    if (responseData == null ? void 0 : responseData.error) {
      return Promise.reject({
        ...responseData.error,
        status
      });
    }
    if (responseData == null ? void 0 : responseData.detail) {
      const detail = responseData.detail;
      return Promise.reject({
        code: "API_ERROR",
        message: typeof detail === "string" ? detail : JSON.stringify(detail),
        status
      });
    }
    if (error.code === "ECONNABORTED") {
      return Promise.reject({
        code: "TIMEOUT",
        message: "Request timed out"
      });
    }
    if (!error.response) {
      return Promise.reject({
        code: "NETWORK_ERROR",
        message: "Unable to connect to server"
      });
    }
    return Promise.reject({
      code: "UNKNOWN_ERROR",
      message: error.message || "An unknown error occurred",
      status
    });
  }
);
function extractData(response) {
  return response.data.data;
}
async function getSystemInfo() {
  const response = await apiClient.get("/system/info");
  return extractData(response);
}
async function getHealthStatus() {
  const response = await apiClient.get("/system/health");
  return extractData(response);
}
async function updateStationInfo(data) {
  const response = await apiClient.put("/system/station-info", data);
  return extractData(response);
}
async function getWorkflowConfig() {
  const response = await apiClient.get("/system/workflow");
  return extractData(response);
}
async function updateWorkflowConfig(data) {
  const response = await apiClient.put("/system/workflow", data);
  return extractData(response);
}
async function getOperatorSession() {
  const response = await apiClient.get("/system/operator");
  return extractData(response);
}
async function operatorLogin(data) {
  const response = await apiClient.post("/system/operator-login", data);
  return extractData(response);
}
async function operatorLogout() {
  const response = await apiClient.post("/system/operator-logout");
  return extractData(response);
}
async function getProcesses() {
  const response = await apiClient.get("/system/processes");
  return extractData(response);
}
async function validateWip(wipId, processId) {
  const response = await apiClient.post(
    "/system/validate-wip",
    { wip_id: wipId, process_id: processId }
  );
  return extractData(response);
}
function useSystemInfo() {
  return useQuery({
    queryKey: queryKeys.systemInfo,
    queryFn: getSystemInfo,
    staleTime: POLLING_INTERVALS.systemInfo
  });
}
function useHealthStatus() {
  return useQuery({
    queryKey: queryKeys.healthStatus,
    queryFn: getHealthStatus,
    refetchInterval: POLLING_INTERVALS.health
  });
}
function useUpdateStationInfo() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (data) => updateStationInfo(data),
    onSuccess: (data) => {
      queryClient2.setQueryData(queryKeys.systemInfo, data);
    }
  });
}
function useWorkflowConfig() {
  return useQuery({
    queryKey: queryKeys.workflowConfig,
    queryFn: getWorkflowConfig
  });
}
function useUpdateWorkflowConfig() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (data) => updateWorkflowConfig(data),
    onSuccess: (data) => {
      queryClient2.setQueryData(queryKeys.workflowConfig, data);
    }
  });
}
function useProcesses() {
  return useQuery({
    queryKey: ["system", "processes"],
    queryFn: getProcesses,
    staleTime: 5 * 60 * 1e3
    // Cache for 5 minutes
  });
}
function useOperatorSession() {
  return useQuery({
    queryKey: queryKeys.operatorSession,
    queryFn: getOperatorSession,
    // Refetch on window focus to stay in sync
    refetchOnWindowFocus: true,
    // Don't retry on 401 (not logged in is not an error)
    retry: false
  });
}
function useOperatorLogin() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (data) => operatorLogin(data),
    onSuccess: (data) => {
      queryClient2.setQueryData(queryKeys.operatorSession, data);
    }
  });
}
function useOperatorLogout() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: () => operatorLogout(),
    onSuccess: (data) => {
      queryClient2.setQueryData(queryKeys.operatorSession, data);
    }
  });
}
const scriptRel = "modulepreload";
const assetsURL = function(dep) {
  return "/ui/" + dep;
};
const seen = {};
const __vitePreload = function preload(baseModule, deps, importerUrl) {
  let promise = Promise.resolve();
  if (deps && deps.length > 0) {
    let allSettled2 = function(promises) {
      return Promise.all(
        promises.map(
          (p) => Promise.resolve(p).then(
            (value) => ({ status: "fulfilled", value }),
            (reason) => ({ status: "rejected", reason })
          )
        )
      );
    };
    document.getElementsByTagName("link");
    const cspNonceMeta = document.querySelector(
      "meta[property=csp-nonce]"
    );
    const cspNonce = (cspNonceMeta == null ? void 0 : cspNonceMeta.nonce) || (cspNonceMeta == null ? void 0 : cspNonceMeta.getAttribute("nonce"));
    promise = allSettled2(
      deps.map((dep) => {
        dep = assetsURL(dep);
        if (dep in seen) return;
        seen[dep] = true;
        const isCss = dep.endsWith(".css");
        const cssSelector = isCss ? '[rel="stylesheet"]' : "";
        if (document.querySelector(`link[href="${dep}"]${cssSelector}`)) {
          return;
        }
        const link = document.createElement("link");
        link.rel = isCss ? "stylesheet" : scriptRel;
        if (!isCss) {
          link.as = "script";
        }
        link.crossOrigin = "";
        link.href = dep;
        if (cspNonce) {
          link.setAttribute("nonce", cspNonce);
        }
        document.head.appendChild(link);
        if (isCss) {
          return new Promise((res, rej) => {
            link.addEventListener("load", res);
            link.addEventListener(
              "error",
              () => rej(new Error(`Unable to preload CSS for ${dep}`))
            );
          });
        }
      })
    );
  }
  function handlePreloadError(err) {
    const e = new Event("vite:preloadError", {
      cancelable: true
    });
    e.payload = err;
    window.dispatchEvent(e);
    if (!e.defaultPrevented) {
      throw err;
    }
  }
  return promise.then((res) => {
    for (const item of res || []) {
      if (item.status !== "rejected") continue;
      handlePreloadError(item.reason);
    }
    return baseModule().catch(handlePreloadError);
  });
};
async function getBatches() {
  const response = await apiClient.get("/batches");
  return extractData(response);
}
async function getBatch(batchId) {
  var _a, _b, _c, _d, _e, _f, _g, _h, _i;
  const response = await apiClient.get(`/batches/${batchId}`);
  const data = extractData(response);
  const hardwareStatus = {};
  if (data.hardware) {
    for (const [hwId, hw] of Object.entries(data.hardware)) {
      hardwareStatus[hwId] = {
        id: hwId,
        driver: hw.driver || hw.type || "unknown",
        status: hw.connected ? "connected" : "disconnected",
        connected: hw.connected || false,
        config: hw.details || {}
      };
    }
  }
  const steps = (((_a = data.execution) == null ? void 0 : _a.steps) || []).map((step, index) => ({
    name: step.name,
    order: step.order ?? index + 1,
    // Use index if order not provided
    status: step.status,
    // Determine pass based on status and pass field
    pass: step.pass ?? step.status === "completed",
    duration: step.duration,
    result: step.result
  }));
  const stepNames = steps.map((step) => step.name);
  return {
    id: data.id,
    name: data.name,
    status: data.status,
    sequenceName: ((_b = data.sequence) == null ? void 0 : _b.name) || "",
    sequenceVersion: ((_c = data.sequence) == null ? void 0 : _c.version) || "",
    sequencePackage: ((_d = data.sequence) == null ? void 0 : _d.packagePath) || "",
    currentStep: (_e = data.execution) == null ? void 0 : _e.currentStep,
    stepIndex: ((_f = data.execution) == null ? void 0 : _f.stepIndex) || 0,
    totalSteps: ((_g = data.execution) == null ? void 0 : _g.totalSteps) || steps.length,
    stepNames,
    progress: ((_h = data.execution) == null ? void 0 : _h.progress) || 0,
    startedAt: void 0,
    elapsed: ((_i = data.execution) == null ? void 0 : _i.elapsed) || 0,
    hardwareConfig: {},
    autoStart: false,
    parameters: data.parameters || {},
    hardwareStatus,
    processId: data.processId,
    headerId: data.headerId,
    execution: data.execution ? {
      // Map API status to ExecutionStatus ('running' | 'completed' | 'failed' | 'stopped')
      status: (() => {
        var _a2;
        const s = ((_a2 = data.execution) == null ? void 0 : _a2.status) || "stopped";
        if (s === "idle" || s === "paused") return "stopped";
        if (s === "running" || s === "completed" || s === "failed" || s === "stopped") return s;
        return "stopped";
      })(),
      currentStep: data.execution.currentStep,
      stepIndex: data.execution.stepIndex || 0,
      totalSteps: data.execution.totalSteps || 0,
      progress: data.execution.progress || 0,
      startedAt: data.execution.startedAt ? new Date(data.execution.startedAt) : void 0,
      elapsed: data.execution.elapsed || 0,
      steps
    } : void 0
  };
}
async function startBatch(batchId) {
  const response = await apiClient.post(
    `/batches/${batchId}/start`
  );
  return extractData(response);
}
async function stopBatch(batchId) {
  const response = await apiClient.post(
    `/batches/${batchId}/stop`
  );
  return extractData(response);
}
async function deleteBatch(batchId) {
  const response = await apiClient.delete(
    `/batches/${batchId}`
  );
  return extractData(response);
}
async function startSequence(batchId, request) {
  const response = await apiClient.post(
    `/batches/${batchId}/sequence/start`,
    request
  );
  return extractData(response);
}
async function stopSequence(batchId) {
  const response = await apiClient.post(
    `/batches/${batchId}/sequence/stop`
  );
  return extractData(response);
}
async function manualControl(batchId, request) {
  const response = await apiClient.post(
    `/batches/${batchId}/manual`,
    request
  );
  return extractData(response);
}
async function createBatches(request) {
  const batchIds = [];
  const timestamp = (/* @__PURE__ */ new Date()).toISOString();
  for (let i = 0; i < request.quantity; i++) {
    const batchId = `batch-${Date.now()}-${Math.random().toString(36).substring(2, 9)}-${i}`;
    const batchName = request.quantity > 1 ? `${request.sequenceName} #${i + 1}` : request.sequenceName;
    const serverRequest = {
      id: batchId,
      name: batchName,
      sequence_package: request.sequenceName,
      hardware: {},
      auto_start: false
    };
    const response = await apiClient.post(
      "/batches",
      serverRequest
    );
    const data = extractData(response);
    batchIds.push(data.batch_id);
  }
  return {
    batchIds,
    sequenceName: request.sequenceName,
    createdAt: timestamp
  };
}
async function updateBatch(batchId, request) {
  const serverRequest = {};
  if (request.name !== void 0) serverRequest.name = request.name;
  if (request.sequencePackage !== void 0) serverRequest.sequence_package = request.sequencePackage;
  if (request.hardware !== void 0) serverRequest.hardware = request.hardware;
  if (request.autoStart !== void 0) serverRequest.auto_start = request.autoStart;
  if (request.processId !== void 0) serverRequest.process_id = request.processId;
  if (request.headerId !== void 0) serverRequest.header_id = request.headerId;
  if (request.parameters !== void 0) serverRequest.parameters = request.parameters;
  const response = await apiClient.put(
    `/batches/${batchId}`,
    serverRequest
  );
  return extractData(response);
}
async function getBatchStatistics(batchId) {
  const response = await apiClient.get(
    `/batches/${batchId}/statistics`
  );
  return extractData(response);
}
async function getAllBatchStatistics() {
  const response = await apiClient.get(
    "/batches/statistics"
  );
  return extractData(response);
}
const batches = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  createBatches,
  deleteBatch,
  getAllBatchStatistics,
  getBatch,
  getBatchStatistics,
  getBatches,
  manualControl,
  startBatch,
  startSequence,
  stopBatch,
  stopSequence,
  updateBatch
}, Symbol.toStringTag, { value: "Module" }));
function isAlreadyRunningError(error) {
  if (error && typeof error === "object" && "status" in error) {
    return error.status === 409;
  }
  return false;
}
function useBatchList() {
  const setBatches = useBatchStore((state) => state.setBatches);
  const pollingFallbackActive = useConnectionStore((state) => state.pollingFallbackActive);
  const pollingInterval = pollingFallbackActive ? POLLING_INTERVALS.batchesFallback : POLLING_INTERVALS.batches;
  const query = useQuery({
    queryKey: queryKeys.batches,
    queryFn: getBatches,
    refetchInterval: pollingInterval
  });
  reactExports.useEffect(() => {
    if (query.data) {
      setBatches(query.data);
    }
  }, [query.data, setBatches]);
  return query;
}
function useBatch(batchId) {
  const storeBatch = useBatchStore(
    (state) => batchId ? state.batches.get(batchId) : void 0
  );
  const query = useQuery({
    queryKey: queryKeys.batch(batchId ?? ""),
    queryFn: () => getBatch(batchId),
    enabled: !!batchId,
    // Disable polling during active execution or transitions (WebSocket handles updates)
    // Resume polling when idle or completed for eventual consistency
    refetchInterval: () => {
      if ((storeBatch == null ? void 0 : storeBatch.status) === "running" || (storeBatch == null ? void 0 : storeBatch.status) === "starting" || (storeBatch == null ? void 0 : storeBatch.status) === "stopping") {
        return false;
      }
      return POLLING_INTERVALS.batchDetail;
    }
  });
  reactExports.useEffect(() => {
    if (query.data && batchId) {
      useBatchStore.getState().setBatches([query.data]);
    }
  }, [query.data, batchId]);
  const mergedData = reactExports.useMemo(() => {
    if (!batchId) return void 0;
    if (!query.data && !storeBatch) return void 0;
    if (storeBatch && query.data) {
      return {
        ...query.data,
        // Real-time fields from store take priority
        status: storeBatch.status,
        progress: storeBatch.progress,
        currentStep: storeBatch.currentStep,
        stepIndex: storeBatch.stepIndex,
        executionId: storeBatch.executionId,
        lastRunPassed: storeBatch.lastRunPassed,
        // Include steps from store for real-time step updates
        steps: storeBatch.steps,
        // Include elapsed time from store (updated via WebSocket sequence_complete)
        elapsed: storeBatch.elapsed
      };
    }
    return query.data ?? storeBatch;
  }, [batchId, storeBatch, query.data]);
  return {
    ...query,
    data: mergedData
  };
}
function useStartBatch() {
  const queryClient2 = useQueryClient();
  const updateBatchStatus = useBatchStore((state) => state.updateBatchStatus);
  return useMutation({
    mutationFn: async (batchId) => {
      try {
        return await startBatch(batchId);
      } catch (error) {
        if (isAlreadyRunningError(error)) {
          return { batchId, status: "already_running", message: "Batch already running" };
        }
        throw error;
      }
    },
    onMutate: async (batchId) => {
      await queryClient2.cancelQueries({ queryKey: queryKeys.batch(batchId) });
      await queryClient2.cancelQueries({ queryKey: queryKeys.batches });
      const batch = useBatchStore.getState().batches.get(batchId);
      const previousStatus = (batch == null ? void 0 : batch.status) ?? "idle";
      updateBatchStatus(batchId, "starting");
      return { batchId, previousStatus };
    },
    onSuccess: (result) => {
      queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
      if ("status" in result && result.status === "already_running") ;
      else {
        toast.success("Batch started successfully");
      }
    },
    onError: (error, batchId, context) => {
      if (context == null ? void 0 : context.previousStatus) {
        updateBatchStatus(batchId, context.previousStatus);
      }
      toast.error(`Failed to start batch: ${getErrorMessage(error)}`);
    }
  });
}
function useStopBatch() {
  const queryClient2 = useQueryClient();
  const updateBatchStatus = useBatchStore((state) => state.updateBatchStatus);
  return useMutation({
    mutationFn: (batchId) => stopBatch(batchId),
    onMutate: async (batchId) => {
      await queryClient2.cancelQueries({ queryKey: queryKeys.batch(batchId) });
      await queryClient2.cancelQueries({ queryKey: queryKeys.batches });
      const batch = useBatchStore.getState().batches.get(batchId);
      const previousStatus = (batch == null ? void 0 : batch.status) ?? "running";
      updateBatchStatus(batchId, "stopping");
      return { batchId, previousStatus };
    },
    onSuccess: (_, batchId) => {
      updateBatchStatus(batchId, "idle");
      queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success("Batch stopped successfully");
    },
    onError: (error, batchId, context) => {
      if (context == null ? void 0 : context.previousStatus) {
        updateBatchStatus(batchId, context.previousStatus);
      }
      toast.error(`Failed to stop batch: ${getErrorMessage(error)}`);
    }
  });
}
function useDeleteBatch() {
  const queryClient2 = useQueryClient();
  const removeBatch = useBatchStore((state) => state.removeBatch);
  return useMutation({
    mutationFn: async (batchId) => {
      const { deleteBatch: deleteBatch2 } = await __vitePreload(async () => {
        const { deleteBatch: deleteBatch3 } = await Promise.resolve().then(() => batches);
        return { deleteBatch: deleteBatch3 };
      }, true ? void 0 : void 0);
      return deleteBatch2(batchId);
    },
    onSuccess: (_, batchId) => {
      removeBatch(batchId);
      queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success("Batch deleted successfully");
    },
    onError: (error) => {
      toast.error(`Failed to delete batch: ${getErrorMessage(error)}`);
    }
  });
}
function useStartSequence() {
  const queryClient2 = useQueryClient();
  const updateBatchStatus = useBatchStore((state) => state.updateBatchStatus);
  return useMutation({
    mutationFn: async ({
      batchId,
      request
    }) => {
      try {
        return await startSequence(batchId, request);
      } catch (error) {
        if (isAlreadyRunningError(error)) {
          return { batchId, status: "already_running", message: "Sequence already running" };
        }
        throw error;
      }
    },
    onMutate: async ({ batchId }) => {
      await queryClient2.cancelQueries({ queryKey: queryKeys.batch(batchId) });
      await queryClient2.cancelQueries({ queryKey: queryKeys.batches });
      const batch = useBatchStore.getState().batches.get(batchId);
      const previousStatus = (batch == null ? void 0 : batch.status) ?? "idle";
      updateBatchStatus(batchId, "starting");
      return { batchId, previousStatus };
    },
    onSuccess: (result, variables) => {
      queryClient2.invalidateQueries({ queryKey: queryKeys.batch(variables.batchId) });
      queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
      if ("status" in result && result.status === "already_running") ;
      else {
        toast.success("Sequence started successfully");
      }
    },
    onError: (error, variables, context) => {
      if (context == null ? void 0 : context.previousStatus) {
        updateBatchStatus(variables.batchId, context.previousStatus);
      }
      toast.error(`Failed to start sequence: ${getErrorMessage(error)}`);
    }
  });
}
function useStopSequence() {
  const queryClient2 = useQueryClient();
  const updateBatchStatus = useBatchStore((state) => state.updateBatchStatus);
  return useMutation({
    mutationFn: (batchId) => stopSequence(batchId),
    onMutate: async (batchId) => {
      await queryClient2.cancelQueries({ queryKey: queryKeys.batch(batchId) });
      await queryClient2.cancelQueries({ queryKey: queryKeys.batches });
      const batch = useBatchStore.getState().batches.get(batchId);
      const previousStatus = (batch == null ? void 0 : batch.status) ?? "running";
      updateBatchStatus(batchId, "stopping");
      return { batchId, previousStatus };
    },
    onSuccess: (_, batchId) => {
      updateBatchStatus(batchId, "idle");
      queryClient2.invalidateQueries({ queryKey: queryKeys.batch(batchId) });
      queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success("Sequence stopped successfully");
    },
    onError: (error, batchId, context) => {
      if (context == null ? void 0 : context.previousStatus) {
        updateBatchStatus(batchId, context.previousStatus);
      }
      toast.error(`Failed to stop sequence: ${getErrorMessage(error)}`);
    }
  });
}
function useCreateBatches() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (request) => createBatches(request),
    onSuccess: (data) => {
      queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success(`Created ${data.batchIds.length} batch(es) successfully`);
    },
    onError: (error) => {
      toast.error(`Failed to create batches: ${getErrorMessage(error)}`);
    }
  });
}
function useBatchStatistics(batchId) {
  return useQuery({
    queryKey: queryKeys.batchStatistics(batchId ?? ""),
    queryFn: () => getBatchStatistics(batchId),
    enabled: !!batchId,
    staleTime: 10 * 1e3
    // 10 seconds - shorter for real-time updates
  });
}
function useAllBatchStatistics() {
  return useQuery({
    queryKey: queryKeys.allBatchStatistics,
    queryFn: getAllBatchStatistics,
    staleTime: 10 * 1e3,
    // 10 seconds - shorter for real-time updates
    retry: false,
    // Don't retry on 404
    throwOnError: false
    // Don't throw errors
  });
}
function useUpdateBatch() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: ({
      batchId,
      request
    }) => updateBatch(batchId, request),
    onSuccess: (_, variables) => {
      queryClient2.invalidateQueries({ queryKey: queryKeys.batch(variables.batchId) });
      queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
    },
    onError: (error) => {
      toast.error(`Failed to update batch: ${getErrorMessage(error)}`);
    }
  });
}
function commonjsRequire(path) {
  throw new Error('Could not dynamically require "' + path + '". Please configure the dynamicRequireTargets or/and ignoreDynamicRequires option of @rollup/plugin-commonjs appropriately for this require call to work.');
}
var jszip_min = { exports: {} };
/*!

JSZip v3.10.1 - A JavaScript class for generating and reading zip files
<http://stuartk.com/jszip>

(c) 2009-2016 Stuart Knightley <stuart [at] stuartk.com>
Dual licenced under the MIT license or GPLv3. See https://raw.github.com/Stuk/jszip/main/LICENSE.markdown.

JSZip uses the library pako released under the MIT license :
https://github.com/nodeca/pako/blob/main/LICENSE
*/
var hasRequiredJszip_min;
function requireJszip_min() {
  if (hasRequiredJszip_min) return jszip_min.exports;
  hasRequiredJszip_min = 1;
  (function(module, exports$1) {
    !(function(e) {
      module.exports = e();
    })(function() {
      return (function s(a, o, h) {
        function u(r, e2) {
          if (!o[r]) {
            if (!a[r]) {
              var t = "function" == typeof commonjsRequire && commonjsRequire;
              if (!e2 && t) return t(r, true);
              if (l) return l(r, true);
              var n = new Error("Cannot find module '" + r + "'");
              throw n.code = "MODULE_NOT_FOUND", n;
            }
            var i = o[r] = { exports: {} };
            a[r][0].call(i.exports, function(e3) {
              var t2 = a[r][1][e3];
              return u(t2 || e3);
            }, i, i.exports, s, a, o, h);
          }
          return o[r].exports;
        }
        for (var l = "function" == typeof commonjsRequire && commonjsRequire, e = 0; e < h.length; e++) u(h[e]);
        return u;
      })({ 1: [function(e, t, r) {
        var d = e("./utils"), c = e("./support"), p = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
        r.encode = function(e2) {
          for (var t2, r2, n, i, s, a, o, h = [], u = 0, l = e2.length, f = l, c2 = "string" !== d.getTypeOf(e2); u < e2.length; ) f = l - u, n = c2 ? (t2 = e2[u++], r2 = u < l ? e2[u++] : 0, u < l ? e2[u++] : 0) : (t2 = e2.charCodeAt(u++), r2 = u < l ? e2.charCodeAt(u++) : 0, u < l ? e2.charCodeAt(u++) : 0), i = t2 >> 2, s = (3 & t2) << 4 | r2 >> 4, a = 1 < f ? (15 & r2) << 2 | n >> 6 : 64, o = 2 < f ? 63 & n : 64, h.push(p.charAt(i) + p.charAt(s) + p.charAt(a) + p.charAt(o));
          return h.join("");
        }, r.decode = function(e2) {
          var t2, r2, n, i, s, a, o = 0, h = 0, u = "data:";
          if (e2.substr(0, u.length) === u) throw new Error("Invalid base64 input, it looks like a data url.");
          var l, f = 3 * (e2 = e2.replace(/[^A-Za-z0-9+/=]/g, "")).length / 4;
          if (e2.charAt(e2.length - 1) === p.charAt(64) && f--, e2.charAt(e2.length - 2) === p.charAt(64) && f--, f % 1 != 0) throw new Error("Invalid base64 input, bad content length.");
          for (l = c.uint8array ? new Uint8Array(0 | f) : new Array(0 | f); o < e2.length; ) t2 = p.indexOf(e2.charAt(o++)) << 2 | (i = p.indexOf(e2.charAt(o++))) >> 4, r2 = (15 & i) << 4 | (s = p.indexOf(e2.charAt(o++))) >> 2, n = (3 & s) << 6 | (a = p.indexOf(e2.charAt(o++))), l[h++] = t2, 64 !== s && (l[h++] = r2), 64 !== a && (l[h++] = n);
          return l;
        };
      }, { "./support": 30, "./utils": 32 }], 2: [function(e, t, r) {
        var n = e("./external"), i = e("./stream/DataWorker"), s = e("./stream/Crc32Probe"), a = e("./stream/DataLengthProbe");
        function o(e2, t2, r2, n2, i2) {
          this.compressedSize = e2, this.uncompressedSize = t2, this.crc32 = r2, this.compression = n2, this.compressedContent = i2;
        }
        o.prototype = { getContentWorker: function() {
          var e2 = new i(n.Promise.resolve(this.compressedContent)).pipe(this.compression.uncompressWorker()).pipe(new a("data_length")), t2 = this;
          return e2.on("end", function() {
            if (this.streamInfo.data_length !== t2.uncompressedSize) throw new Error("Bug : uncompressed data size mismatch");
          }), e2;
        }, getCompressedWorker: function() {
          return new i(n.Promise.resolve(this.compressedContent)).withStreamInfo("compressedSize", this.compressedSize).withStreamInfo("uncompressedSize", this.uncompressedSize).withStreamInfo("crc32", this.crc32).withStreamInfo("compression", this.compression);
        } }, o.createWorkerFrom = function(e2, t2, r2) {
          return e2.pipe(new s()).pipe(new a("uncompressedSize")).pipe(t2.compressWorker(r2)).pipe(new a("compressedSize")).withStreamInfo("compression", t2);
        }, t.exports = o;
      }, { "./external": 6, "./stream/Crc32Probe": 25, "./stream/DataLengthProbe": 26, "./stream/DataWorker": 27 }], 3: [function(e, t, r) {
        var n = e("./stream/GenericWorker");
        r.STORE = { magic: "\0\0", compressWorker: function() {
          return new n("STORE compression");
        }, uncompressWorker: function() {
          return new n("STORE decompression");
        } }, r.DEFLATE = e("./flate");
      }, { "./flate": 7, "./stream/GenericWorker": 28 }], 4: [function(e, t, r) {
        var n = e("./utils");
        var o = (function() {
          for (var e2, t2 = [], r2 = 0; r2 < 256; r2++) {
            e2 = r2;
            for (var n2 = 0; n2 < 8; n2++) e2 = 1 & e2 ? 3988292384 ^ e2 >>> 1 : e2 >>> 1;
            t2[r2] = e2;
          }
          return t2;
        })();
        t.exports = function(e2, t2) {
          return void 0 !== e2 && e2.length ? "string" !== n.getTypeOf(e2) ? (function(e3, t3, r2, n2) {
            var i = o, s = n2 + r2;
            e3 ^= -1;
            for (var a = n2; a < s; a++) e3 = e3 >>> 8 ^ i[255 & (e3 ^ t3[a])];
            return -1 ^ e3;
          })(0 | t2, e2, e2.length, 0) : (function(e3, t3, r2, n2) {
            var i = o, s = n2 + r2;
            e3 ^= -1;
            for (var a = n2; a < s; a++) e3 = e3 >>> 8 ^ i[255 & (e3 ^ t3.charCodeAt(a))];
            return -1 ^ e3;
          })(0 | t2, e2, e2.length, 0) : 0;
        };
      }, { "./utils": 32 }], 5: [function(e, t, r) {
        r.base64 = false, r.binary = false, r.dir = false, r.createFolders = true, r.date = null, r.compression = null, r.compressionOptions = null, r.comment = null, r.unixPermissions = null, r.dosPermissions = null;
      }, {}], 6: [function(e, t, r) {
        var n = null;
        n = "undefined" != typeof Promise ? Promise : e("lie"), t.exports = { Promise: n };
      }, { lie: 37 }], 7: [function(e, t, r) {
        var n = "undefined" != typeof Uint8Array && "undefined" != typeof Uint16Array && "undefined" != typeof Uint32Array, i = e("pako"), s = e("./utils"), a = e("./stream/GenericWorker"), o = n ? "uint8array" : "array";
        function h(e2, t2) {
          a.call(this, "FlateWorker/" + e2), this._pako = null, this._pakoAction = e2, this._pakoOptions = t2, this.meta = {};
        }
        r.magic = "\b\0", s.inherits(h, a), h.prototype.processChunk = function(e2) {
          this.meta = e2.meta, null === this._pako && this._createPako(), this._pako.push(s.transformTo(o, e2.data), false);
        }, h.prototype.flush = function() {
          a.prototype.flush.call(this), null === this._pako && this._createPako(), this._pako.push([], true);
        }, h.prototype.cleanUp = function() {
          a.prototype.cleanUp.call(this), this._pako = null;
        }, h.prototype._createPako = function() {
          this._pako = new i[this._pakoAction]({ raw: true, level: this._pakoOptions.level || -1 });
          var t2 = this;
          this._pako.onData = function(e2) {
            t2.push({ data: e2, meta: t2.meta });
          };
        }, r.compressWorker = function(e2) {
          return new h("Deflate", e2);
        }, r.uncompressWorker = function() {
          return new h("Inflate", {});
        };
      }, { "./stream/GenericWorker": 28, "./utils": 32, pako: 38 }], 8: [function(e, t, r) {
        function A(e2, t2) {
          var r2, n2 = "";
          for (r2 = 0; r2 < t2; r2++) n2 += String.fromCharCode(255 & e2), e2 >>>= 8;
          return n2;
        }
        function n(e2, t2, r2, n2, i2, s2) {
          var a, o, h = e2.file, u = e2.compression, l = s2 !== O.utf8encode, f = I.transformTo("string", s2(h.name)), c = I.transformTo("string", O.utf8encode(h.name)), d = h.comment, p = I.transformTo("string", s2(d)), m = I.transformTo("string", O.utf8encode(d)), _ = c.length !== h.name.length, g = m.length !== d.length, b = "", v = "", y = "", w = h.dir, k = h.date, x = { crc32: 0, compressedSize: 0, uncompressedSize: 0 };
          t2 && !r2 || (x.crc32 = e2.crc32, x.compressedSize = e2.compressedSize, x.uncompressedSize = e2.uncompressedSize);
          var S = 0;
          t2 && (S |= 8), l || !_ && !g || (S |= 2048);
          var z = 0, C = 0;
          w && (z |= 16), "UNIX" === i2 ? (C = 798, z |= (function(e3, t3) {
            var r3 = e3;
            return e3 || (r3 = t3 ? 16893 : 33204), (65535 & r3) << 16;
          })(h.unixPermissions, w)) : (C = 20, z |= (function(e3) {
            return 63 & (e3 || 0);
          })(h.dosPermissions)), a = k.getUTCHours(), a <<= 6, a |= k.getUTCMinutes(), a <<= 5, a |= k.getUTCSeconds() / 2, o = k.getUTCFullYear() - 1980, o <<= 4, o |= k.getUTCMonth() + 1, o <<= 5, o |= k.getUTCDate(), _ && (v = A(1, 1) + A(B(f), 4) + c, b += "up" + A(v.length, 2) + v), g && (y = A(1, 1) + A(B(p), 4) + m, b += "uc" + A(y.length, 2) + y);
          var E = "";
          return E += "\n\0", E += A(S, 2), E += u.magic, E += A(a, 2), E += A(o, 2), E += A(x.crc32, 4), E += A(x.compressedSize, 4), E += A(x.uncompressedSize, 4), E += A(f.length, 2), E += A(b.length, 2), { fileRecord: R.LOCAL_FILE_HEADER + E + f + b, dirRecord: R.CENTRAL_FILE_HEADER + A(C, 2) + E + A(p.length, 2) + "\0\0\0\0" + A(z, 4) + A(n2, 4) + f + b + p };
        }
        var I = e("../utils"), i = e("../stream/GenericWorker"), O = e("../utf8"), B = e("../crc32"), R = e("../signature");
        function s(e2, t2, r2, n2) {
          i.call(this, "ZipFileWorker"), this.bytesWritten = 0, this.zipComment = t2, this.zipPlatform = r2, this.encodeFileName = n2, this.streamFiles = e2, this.accumulate = false, this.contentBuffer = [], this.dirRecords = [], this.currentSourceOffset = 0, this.entriesCount = 0, this.currentFile = null, this._sources = [];
        }
        I.inherits(s, i), s.prototype.push = function(e2) {
          var t2 = e2.meta.percent || 0, r2 = this.entriesCount, n2 = this._sources.length;
          this.accumulate ? this.contentBuffer.push(e2) : (this.bytesWritten += e2.data.length, i.prototype.push.call(this, { data: e2.data, meta: { currentFile: this.currentFile, percent: r2 ? (t2 + 100 * (r2 - n2 - 1)) / r2 : 100 } }));
        }, s.prototype.openedSource = function(e2) {
          this.currentSourceOffset = this.bytesWritten, this.currentFile = e2.file.name;
          var t2 = this.streamFiles && !e2.file.dir;
          if (t2) {
            var r2 = n(e2, t2, false, this.currentSourceOffset, this.zipPlatform, this.encodeFileName);
            this.push({ data: r2.fileRecord, meta: { percent: 0 } });
          } else this.accumulate = true;
        }, s.prototype.closedSource = function(e2) {
          this.accumulate = false;
          var t2 = this.streamFiles && !e2.file.dir, r2 = n(e2, t2, true, this.currentSourceOffset, this.zipPlatform, this.encodeFileName);
          if (this.dirRecords.push(r2.dirRecord), t2) this.push({ data: (function(e3) {
            return R.DATA_DESCRIPTOR + A(e3.crc32, 4) + A(e3.compressedSize, 4) + A(e3.uncompressedSize, 4);
          })(e2), meta: { percent: 100 } });
          else for (this.push({ data: r2.fileRecord, meta: { percent: 0 } }); this.contentBuffer.length; ) this.push(this.contentBuffer.shift());
          this.currentFile = null;
        }, s.prototype.flush = function() {
          for (var e2 = this.bytesWritten, t2 = 0; t2 < this.dirRecords.length; t2++) this.push({ data: this.dirRecords[t2], meta: { percent: 100 } });
          var r2 = this.bytesWritten - e2, n2 = (function(e3, t3, r3, n3, i2) {
            var s2 = I.transformTo("string", i2(n3));
            return R.CENTRAL_DIRECTORY_END + "\0\0\0\0" + A(e3, 2) + A(e3, 2) + A(t3, 4) + A(r3, 4) + A(s2.length, 2) + s2;
          })(this.dirRecords.length, r2, e2, this.zipComment, this.encodeFileName);
          this.push({ data: n2, meta: { percent: 100 } });
        }, s.prototype.prepareNextSource = function() {
          this.previous = this._sources.shift(), this.openedSource(this.previous.streamInfo), this.isPaused ? this.previous.pause() : this.previous.resume();
        }, s.prototype.registerPrevious = function(e2) {
          this._sources.push(e2);
          var t2 = this;
          return e2.on("data", function(e3) {
            t2.processChunk(e3);
          }), e2.on("end", function() {
            t2.closedSource(t2.previous.streamInfo), t2._sources.length ? t2.prepareNextSource() : t2.end();
          }), e2.on("error", function(e3) {
            t2.error(e3);
          }), this;
        }, s.prototype.resume = function() {
          return !!i.prototype.resume.call(this) && (!this.previous && this._sources.length ? (this.prepareNextSource(), true) : this.previous || this._sources.length || this.generatedError ? void 0 : (this.end(), true));
        }, s.prototype.error = function(e2) {
          var t2 = this._sources;
          if (!i.prototype.error.call(this, e2)) return false;
          for (var r2 = 0; r2 < t2.length; r2++) try {
            t2[r2].error(e2);
          } catch (e3) {
          }
          return true;
        }, s.prototype.lock = function() {
          i.prototype.lock.call(this);
          for (var e2 = this._sources, t2 = 0; t2 < e2.length; t2++) e2[t2].lock();
        }, t.exports = s;
      }, { "../crc32": 4, "../signature": 23, "../stream/GenericWorker": 28, "../utf8": 31, "../utils": 32 }], 9: [function(e, t, r) {
        var u = e("../compressions"), n = e("./ZipFileWorker");
        r.generateWorker = function(e2, a, t2) {
          var o = new n(a.streamFiles, t2, a.platform, a.encodeFileName), h = 0;
          try {
            e2.forEach(function(e3, t3) {
              h++;
              var r2 = (function(e4, t4) {
                var r3 = e4 || t4, n3 = u[r3];
                if (!n3) throw new Error(r3 + " is not a valid compression method !");
                return n3;
              })(t3.options.compression, a.compression), n2 = t3.options.compressionOptions || a.compressionOptions || {}, i = t3.dir, s = t3.date;
              t3._compressWorker(r2, n2).withStreamInfo("file", { name: e3, dir: i, date: s, comment: t3.comment || "", unixPermissions: t3.unixPermissions, dosPermissions: t3.dosPermissions }).pipe(o);
            }), o.entriesCount = h;
          } catch (e3) {
            o.error(e3);
          }
          return o;
        };
      }, { "../compressions": 3, "./ZipFileWorker": 8 }], 10: [function(e, t, r) {
        function n() {
          if (!(this instanceof n)) return new n();
          if (arguments.length) throw new Error("The constructor with parameters has been removed in JSZip 3.0, please check the upgrade guide.");
          this.files = /* @__PURE__ */ Object.create(null), this.comment = null, this.root = "", this.clone = function() {
            var e2 = new n();
            for (var t2 in this) "function" != typeof this[t2] && (e2[t2] = this[t2]);
            return e2;
          };
        }
        (n.prototype = e("./object")).loadAsync = e("./load"), n.support = e("./support"), n.defaults = e("./defaults"), n.version = "3.10.1", n.loadAsync = function(e2, t2) {
          return new n().loadAsync(e2, t2);
        }, n.external = e("./external"), t.exports = n;
      }, { "./defaults": 5, "./external": 6, "./load": 11, "./object": 15, "./support": 30 }], 11: [function(e, t, r) {
        var u = e("./utils"), i = e("./external"), n = e("./utf8"), s = e("./zipEntries"), a = e("./stream/Crc32Probe"), l = e("./nodejsUtils");
        function f(n2) {
          return new i.Promise(function(e2, t2) {
            var r2 = n2.decompressed.getContentWorker().pipe(new a());
            r2.on("error", function(e3) {
              t2(e3);
            }).on("end", function() {
              r2.streamInfo.crc32 !== n2.decompressed.crc32 ? t2(new Error("Corrupted zip : CRC32 mismatch")) : e2();
            }).resume();
          });
        }
        t.exports = function(e2, o) {
          var h = this;
          return o = u.extend(o || {}, { base64: false, checkCRC32: false, optimizedBinaryString: false, createFolders: false, decodeFileName: n.utf8decode }), l.isNode && l.isStream(e2) ? i.Promise.reject(new Error("JSZip can't accept a stream when loading a zip file.")) : u.prepareContent("the loaded zip file", e2, true, o.optimizedBinaryString, o.base64).then(function(e3) {
            var t2 = new s(o);
            return t2.load(e3), t2;
          }).then(function(e3) {
            var t2 = [i.Promise.resolve(e3)], r2 = e3.files;
            if (o.checkCRC32) for (var n2 = 0; n2 < r2.length; n2++) t2.push(f(r2[n2]));
            return i.Promise.all(t2);
          }).then(function(e3) {
            for (var t2 = e3.shift(), r2 = t2.files, n2 = 0; n2 < r2.length; n2++) {
              var i2 = r2[n2], s2 = i2.fileNameStr, a2 = u.resolve(i2.fileNameStr);
              h.file(a2, i2.decompressed, { binary: true, optimizedBinaryString: true, date: i2.date, dir: i2.dir, comment: i2.fileCommentStr.length ? i2.fileCommentStr : null, unixPermissions: i2.unixPermissions, dosPermissions: i2.dosPermissions, createFolders: o.createFolders }), i2.dir || (h.file(a2).unsafeOriginalName = s2);
            }
            return t2.zipComment.length && (h.comment = t2.zipComment), h;
          });
        };
      }, { "./external": 6, "./nodejsUtils": 14, "./stream/Crc32Probe": 25, "./utf8": 31, "./utils": 32, "./zipEntries": 33 }], 12: [function(e, t, r) {
        var n = e("../utils"), i = e("../stream/GenericWorker");
        function s(e2, t2) {
          i.call(this, "Nodejs stream input adapter for " + e2), this._upstreamEnded = false, this._bindStream(t2);
        }
        n.inherits(s, i), s.prototype._bindStream = function(e2) {
          var t2 = this;
          (this._stream = e2).pause(), e2.on("data", function(e3) {
            t2.push({ data: e3, meta: { percent: 0 } });
          }).on("error", function(e3) {
            t2.isPaused ? this.generatedError = e3 : t2.error(e3);
          }).on("end", function() {
            t2.isPaused ? t2._upstreamEnded = true : t2.end();
          });
        }, s.prototype.pause = function() {
          return !!i.prototype.pause.call(this) && (this._stream.pause(), true);
        }, s.prototype.resume = function() {
          return !!i.prototype.resume.call(this) && (this._upstreamEnded ? this.end() : this._stream.resume(), true);
        }, t.exports = s;
      }, { "../stream/GenericWorker": 28, "../utils": 32 }], 13: [function(e, t, r) {
        var i = e("readable-stream").Readable;
        function n(e2, t2, r2) {
          i.call(this, t2), this._helper = e2;
          var n2 = this;
          e2.on("data", function(e3, t3) {
            n2.push(e3) || n2._helper.pause(), r2 && r2(t3);
          }).on("error", function(e3) {
            n2.emit("error", e3);
          }).on("end", function() {
            n2.push(null);
          });
        }
        e("../utils").inherits(n, i), n.prototype._read = function() {
          this._helper.resume();
        }, t.exports = n;
      }, { "../utils": 32, "readable-stream": 16 }], 14: [function(e, t, r) {
        t.exports = { isNode: "undefined" != typeof Buffer, newBufferFrom: function(e2, t2) {
          if (Buffer.from && Buffer.from !== Uint8Array.from) return Buffer.from(e2, t2);
          if ("number" == typeof e2) throw new Error('The "data" argument must not be a number');
          return new Buffer(e2, t2);
        }, allocBuffer: function(e2) {
          if (Buffer.alloc) return Buffer.alloc(e2);
          var t2 = new Buffer(e2);
          return t2.fill(0), t2;
        }, isBuffer: function(e2) {
          return Buffer.isBuffer(e2);
        }, isStream: function(e2) {
          return e2 && "function" == typeof e2.on && "function" == typeof e2.pause && "function" == typeof e2.resume;
        } };
      }, {}], 15: [function(e, t, r) {
        function s(e2, t2, r2) {
          var n2, i2 = u.getTypeOf(t2), s2 = u.extend(r2 || {}, f);
          s2.date = s2.date || /* @__PURE__ */ new Date(), null !== s2.compression && (s2.compression = s2.compression.toUpperCase()), "string" == typeof s2.unixPermissions && (s2.unixPermissions = parseInt(s2.unixPermissions, 8)), s2.unixPermissions && 16384 & s2.unixPermissions && (s2.dir = true), s2.dosPermissions && 16 & s2.dosPermissions && (s2.dir = true), s2.dir && (e2 = g(e2)), s2.createFolders && (n2 = _(e2)) && b.call(this, n2, true);
          var a2 = "string" === i2 && false === s2.binary && false === s2.base64;
          r2 && void 0 !== r2.binary || (s2.binary = !a2), (t2 instanceof c && 0 === t2.uncompressedSize || s2.dir || !t2 || 0 === t2.length) && (s2.base64 = false, s2.binary = true, t2 = "", s2.compression = "STORE", i2 = "string");
          var o2 = null;
          o2 = t2 instanceof c || t2 instanceof l ? t2 : p.isNode && p.isStream(t2) ? new m(e2, t2) : u.prepareContent(e2, t2, s2.binary, s2.optimizedBinaryString, s2.base64);
          var h2 = new d(e2, o2, s2);
          this.files[e2] = h2;
        }
        var i = e("./utf8"), u = e("./utils"), l = e("./stream/GenericWorker"), a = e("./stream/StreamHelper"), f = e("./defaults"), c = e("./compressedObject"), d = e("./zipObject"), o = e("./generate"), p = e("./nodejsUtils"), m = e("./nodejs/NodejsStreamInputAdapter"), _ = function(e2) {
          "/" === e2.slice(-1) && (e2 = e2.substring(0, e2.length - 1));
          var t2 = e2.lastIndexOf("/");
          return 0 < t2 ? e2.substring(0, t2) : "";
        }, g = function(e2) {
          return "/" !== e2.slice(-1) && (e2 += "/"), e2;
        }, b = function(e2, t2) {
          return t2 = void 0 !== t2 ? t2 : f.createFolders, e2 = g(e2), this.files[e2] || s.call(this, e2, null, { dir: true, createFolders: t2 }), this.files[e2];
        };
        function h(e2) {
          return "[object RegExp]" === Object.prototype.toString.call(e2);
        }
        var n = { load: function() {
          throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.");
        }, forEach: function(e2) {
          var t2, r2, n2;
          for (t2 in this.files) n2 = this.files[t2], (r2 = t2.slice(this.root.length, t2.length)) && t2.slice(0, this.root.length) === this.root && e2(r2, n2);
        }, filter: function(r2) {
          var n2 = [];
          return this.forEach(function(e2, t2) {
            r2(e2, t2) && n2.push(t2);
          }), n2;
        }, file: function(e2, t2, r2) {
          if (1 !== arguments.length) return e2 = this.root + e2, s.call(this, e2, t2, r2), this;
          if (h(e2)) {
            var n2 = e2;
            return this.filter(function(e3, t3) {
              return !t3.dir && n2.test(e3);
            });
          }
          var i2 = this.files[this.root + e2];
          return i2 && !i2.dir ? i2 : null;
        }, folder: function(r2) {
          if (!r2) return this;
          if (h(r2)) return this.filter(function(e3, t3) {
            return t3.dir && r2.test(e3);
          });
          var e2 = this.root + r2, t2 = b.call(this, e2), n2 = this.clone();
          return n2.root = t2.name, n2;
        }, remove: function(r2) {
          r2 = this.root + r2;
          var e2 = this.files[r2];
          if (e2 || ("/" !== r2.slice(-1) && (r2 += "/"), e2 = this.files[r2]), e2 && !e2.dir) delete this.files[r2];
          else for (var t2 = this.filter(function(e3, t3) {
            return t3.name.slice(0, r2.length) === r2;
          }), n2 = 0; n2 < t2.length; n2++) delete this.files[t2[n2].name];
          return this;
        }, generate: function() {
          throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.");
        }, generateInternalStream: function(e2) {
          var t2, r2 = {};
          try {
            if ((r2 = u.extend(e2 || {}, { streamFiles: false, compression: "STORE", compressionOptions: null, type: "", platform: "DOS", comment: null, mimeType: "application/zip", encodeFileName: i.utf8encode })).type = r2.type.toLowerCase(), r2.compression = r2.compression.toUpperCase(), "binarystring" === r2.type && (r2.type = "string"), !r2.type) throw new Error("No output type specified.");
            u.checkSupport(r2.type), "darwin" !== r2.platform && "freebsd" !== r2.platform && "linux" !== r2.platform && "sunos" !== r2.platform || (r2.platform = "UNIX"), "win32" === r2.platform && (r2.platform = "DOS");
            var n2 = r2.comment || this.comment || "";
            t2 = o.generateWorker(this, r2, n2);
          } catch (e3) {
            (t2 = new l("error")).error(e3);
          }
          return new a(t2, r2.type || "string", r2.mimeType);
        }, generateAsync: function(e2, t2) {
          return this.generateInternalStream(e2).accumulate(t2);
        }, generateNodeStream: function(e2, t2) {
          return (e2 = e2 || {}).type || (e2.type = "nodebuffer"), this.generateInternalStream(e2).toNodejsStream(t2);
        } };
        t.exports = n;
      }, { "./compressedObject": 2, "./defaults": 5, "./generate": 9, "./nodejs/NodejsStreamInputAdapter": 12, "./nodejsUtils": 14, "./stream/GenericWorker": 28, "./stream/StreamHelper": 29, "./utf8": 31, "./utils": 32, "./zipObject": 35 }], 16: [function(e, t, r) {
        t.exports = e("stream");
      }, { stream: void 0 }], 17: [function(e, t, r) {
        var n = e("./DataReader");
        function i(e2) {
          n.call(this, e2);
          for (var t2 = 0; t2 < this.data.length; t2++) e2[t2] = 255 & e2[t2];
        }
        e("../utils").inherits(i, n), i.prototype.byteAt = function(e2) {
          return this.data[this.zero + e2];
        }, i.prototype.lastIndexOfSignature = function(e2) {
          for (var t2 = e2.charCodeAt(0), r2 = e2.charCodeAt(1), n2 = e2.charCodeAt(2), i2 = e2.charCodeAt(3), s = this.length - 4; 0 <= s; --s) if (this.data[s] === t2 && this.data[s + 1] === r2 && this.data[s + 2] === n2 && this.data[s + 3] === i2) return s - this.zero;
          return -1;
        }, i.prototype.readAndCheckSignature = function(e2) {
          var t2 = e2.charCodeAt(0), r2 = e2.charCodeAt(1), n2 = e2.charCodeAt(2), i2 = e2.charCodeAt(3), s = this.readData(4);
          return t2 === s[0] && r2 === s[1] && n2 === s[2] && i2 === s[3];
        }, i.prototype.readData = function(e2) {
          if (this.checkOffset(e2), 0 === e2) return [];
          var t2 = this.data.slice(this.zero + this.index, this.zero + this.index + e2);
          return this.index += e2, t2;
        }, t.exports = i;
      }, { "../utils": 32, "./DataReader": 18 }], 18: [function(e, t, r) {
        var n = e("../utils");
        function i(e2) {
          this.data = e2, this.length = e2.length, this.index = 0, this.zero = 0;
        }
        i.prototype = { checkOffset: function(e2) {
          this.checkIndex(this.index + e2);
        }, checkIndex: function(e2) {
          if (this.length < this.zero + e2 || e2 < 0) throw new Error("End of data reached (data length = " + this.length + ", asked index = " + e2 + "). Corrupted zip ?");
        }, setIndex: function(e2) {
          this.checkIndex(e2), this.index = e2;
        }, skip: function(e2) {
          this.setIndex(this.index + e2);
        }, byteAt: function() {
        }, readInt: function(e2) {
          var t2, r2 = 0;
          for (this.checkOffset(e2), t2 = this.index + e2 - 1; t2 >= this.index; t2--) r2 = (r2 << 8) + this.byteAt(t2);
          return this.index += e2, r2;
        }, readString: function(e2) {
          return n.transformTo("string", this.readData(e2));
        }, readData: function() {
        }, lastIndexOfSignature: function() {
        }, readAndCheckSignature: function() {
        }, readDate: function() {
          var e2 = this.readInt(4);
          return new Date(Date.UTC(1980 + (e2 >> 25 & 127), (e2 >> 21 & 15) - 1, e2 >> 16 & 31, e2 >> 11 & 31, e2 >> 5 & 63, (31 & e2) << 1));
        } }, t.exports = i;
      }, { "../utils": 32 }], 19: [function(e, t, r) {
        var n = e("./Uint8ArrayReader");
        function i(e2) {
          n.call(this, e2);
        }
        e("../utils").inherits(i, n), i.prototype.readData = function(e2) {
          this.checkOffset(e2);
          var t2 = this.data.slice(this.zero + this.index, this.zero + this.index + e2);
          return this.index += e2, t2;
        }, t.exports = i;
      }, { "../utils": 32, "./Uint8ArrayReader": 21 }], 20: [function(e, t, r) {
        var n = e("./DataReader");
        function i(e2) {
          n.call(this, e2);
        }
        e("../utils").inherits(i, n), i.prototype.byteAt = function(e2) {
          return this.data.charCodeAt(this.zero + e2);
        }, i.prototype.lastIndexOfSignature = function(e2) {
          return this.data.lastIndexOf(e2) - this.zero;
        }, i.prototype.readAndCheckSignature = function(e2) {
          return e2 === this.readData(4);
        }, i.prototype.readData = function(e2) {
          this.checkOffset(e2);
          var t2 = this.data.slice(this.zero + this.index, this.zero + this.index + e2);
          return this.index += e2, t2;
        }, t.exports = i;
      }, { "../utils": 32, "./DataReader": 18 }], 21: [function(e, t, r) {
        var n = e("./ArrayReader");
        function i(e2) {
          n.call(this, e2);
        }
        e("../utils").inherits(i, n), i.prototype.readData = function(e2) {
          if (this.checkOffset(e2), 0 === e2) return new Uint8Array(0);
          var t2 = this.data.subarray(this.zero + this.index, this.zero + this.index + e2);
          return this.index += e2, t2;
        }, t.exports = i;
      }, { "../utils": 32, "./ArrayReader": 17 }], 22: [function(e, t, r) {
        var n = e("../utils"), i = e("../support"), s = e("./ArrayReader"), a = e("./StringReader"), o = e("./NodeBufferReader"), h = e("./Uint8ArrayReader");
        t.exports = function(e2) {
          var t2 = n.getTypeOf(e2);
          return n.checkSupport(t2), "string" !== t2 || i.uint8array ? "nodebuffer" === t2 ? new o(e2) : i.uint8array ? new h(n.transformTo("uint8array", e2)) : new s(n.transformTo("array", e2)) : new a(e2);
        };
      }, { "../support": 30, "../utils": 32, "./ArrayReader": 17, "./NodeBufferReader": 19, "./StringReader": 20, "./Uint8ArrayReader": 21 }], 23: [function(e, t, r) {
        r.LOCAL_FILE_HEADER = "PK", r.CENTRAL_FILE_HEADER = "PK", r.CENTRAL_DIRECTORY_END = "PK", r.ZIP64_CENTRAL_DIRECTORY_LOCATOR = "PK\x07", r.ZIP64_CENTRAL_DIRECTORY_END = "PK", r.DATA_DESCRIPTOR = "PK\x07\b";
      }, {}], 24: [function(e, t, r) {
        var n = e("./GenericWorker"), i = e("../utils");
        function s(e2) {
          n.call(this, "ConvertWorker to " + e2), this.destType = e2;
        }
        i.inherits(s, n), s.prototype.processChunk = function(e2) {
          this.push({ data: i.transformTo(this.destType, e2.data), meta: e2.meta });
        }, t.exports = s;
      }, { "../utils": 32, "./GenericWorker": 28 }], 25: [function(e, t, r) {
        var n = e("./GenericWorker"), i = e("../crc32");
        function s() {
          n.call(this, "Crc32Probe"), this.withStreamInfo("crc32", 0);
        }
        e("../utils").inherits(s, n), s.prototype.processChunk = function(e2) {
          this.streamInfo.crc32 = i(e2.data, this.streamInfo.crc32 || 0), this.push(e2);
        }, t.exports = s;
      }, { "../crc32": 4, "../utils": 32, "./GenericWorker": 28 }], 26: [function(e, t, r) {
        var n = e("../utils"), i = e("./GenericWorker");
        function s(e2) {
          i.call(this, "DataLengthProbe for " + e2), this.propName = e2, this.withStreamInfo(e2, 0);
        }
        n.inherits(s, i), s.prototype.processChunk = function(e2) {
          if (e2) {
            var t2 = this.streamInfo[this.propName] || 0;
            this.streamInfo[this.propName] = t2 + e2.data.length;
          }
          i.prototype.processChunk.call(this, e2);
        }, t.exports = s;
      }, { "../utils": 32, "./GenericWorker": 28 }], 27: [function(e, t, r) {
        var n = e("../utils"), i = e("./GenericWorker");
        function s(e2) {
          i.call(this, "DataWorker");
          var t2 = this;
          this.dataIsReady = false, this.index = 0, this.max = 0, this.data = null, this.type = "", this._tickScheduled = false, e2.then(function(e3) {
            t2.dataIsReady = true, t2.data = e3, t2.max = e3 && e3.length || 0, t2.type = n.getTypeOf(e3), t2.isPaused || t2._tickAndRepeat();
          }, function(e3) {
            t2.error(e3);
          });
        }
        n.inherits(s, i), s.prototype.cleanUp = function() {
          i.prototype.cleanUp.call(this), this.data = null;
        }, s.prototype.resume = function() {
          return !!i.prototype.resume.call(this) && (!this._tickScheduled && this.dataIsReady && (this._tickScheduled = true, n.delay(this._tickAndRepeat, [], this)), true);
        }, s.prototype._tickAndRepeat = function() {
          this._tickScheduled = false, this.isPaused || this.isFinished || (this._tick(), this.isFinished || (n.delay(this._tickAndRepeat, [], this), this._tickScheduled = true));
        }, s.prototype._tick = function() {
          if (this.isPaused || this.isFinished) return false;
          var e2 = null, t2 = Math.min(this.max, this.index + 16384);
          if (this.index >= this.max) return this.end();
          switch (this.type) {
            case "string":
              e2 = this.data.substring(this.index, t2);
              break;
            case "uint8array":
              e2 = this.data.subarray(this.index, t2);
              break;
            case "array":
            case "nodebuffer":
              e2 = this.data.slice(this.index, t2);
          }
          return this.index = t2, this.push({ data: e2, meta: { percent: this.max ? this.index / this.max * 100 : 0 } });
        }, t.exports = s;
      }, { "../utils": 32, "./GenericWorker": 28 }], 28: [function(e, t, r) {
        function n(e2) {
          this.name = e2 || "default", this.streamInfo = {}, this.generatedError = null, this.extraStreamInfo = {}, this.isPaused = true, this.isFinished = false, this.isLocked = false, this._listeners = { data: [], end: [], error: [] }, this.previous = null;
        }
        n.prototype = { push: function(e2) {
          this.emit("data", e2);
        }, end: function() {
          if (this.isFinished) return false;
          this.flush();
          try {
            this.emit("end"), this.cleanUp(), this.isFinished = true;
          } catch (e2) {
            this.emit("error", e2);
          }
          return true;
        }, error: function(e2) {
          return !this.isFinished && (this.isPaused ? this.generatedError = e2 : (this.isFinished = true, this.emit("error", e2), this.previous && this.previous.error(e2), this.cleanUp()), true);
        }, on: function(e2, t2) {
          return this._listeners[e2].push(t2), this;
        }, cleanUp: function() {
          this.streamInfo = this.generatedError = this.extraStreamInfo = null, this._listeners = [];
        }, emit: function(e2, t2) {
          if (this._listeners[e2]) for (var r2 = 0; r2 < this._listeners[e2].length; r2++) this._listeners[e2][r2].call(this, t2);
        }, pipe: function(e2) {
          return e2.registerPrevious(this);
        }, registerPrevious: function(e2) {
          if (this.isLocked) throw new Error("The stream '" + this + "' has already been used.");
          this.streamInfo = e2.streamInfo, this.mergeStreamInfo(), this.previous = e2;
          var t2 = this;
          return e2.on("data", function(e3) {
            t2.processChunk(e3);
          }), e2.on("end", function() {
            t2.end();
          }), e2.on("error", function(e3) {
            t2.error(e3);
          }), this;
        }, pause: function() {
          return !this.isPaused && !this.isFinished && (this.isPaused = true, this.previous && this.previous.pause(), true);
        }, resume: function() {
          if (!this.isPaused || this.isFinished) return false;
          var e2 = this.isPaused = false;
          return this.generatedError && (this.error(this.generatedError), e2 = true), this.previous && this.previous.resume(), !e2;
        }, flush: function() {
        }, processChunk: function(e2) {
          this.push(e2);
        }, withStreamInfo: function(e2, t2) {
          return this.extraStreamInfo[e2] = t2, this.mergeStreamInfo(), this;
        }, mergeStreamInfo: function() {
          for (var e2 in this.extraStreamInfo) Object.prototype.hasOwnProperty.call(this.extraStreamInfo, e2) && (this.streamInfo[e2] = this.extraStreamInfo[e2]);
        }, lock: function() {
          if (this.isLocked) throw new Error("The stream '" + this + "' has already been used.");
          this.isLocked = true, this.previous && this.previous.lock();
        }, toString: function() {
          var e2 = "Worker " + this.name;
          return this.previous ? this.previous + " -> " + e2 : e2;
        } }, t.exports = n;
      }, {}], 29: [function(e, t, r) {
        var h = e("../utils"), i = e("./ConvertWorker"), s = e("./GenericWorker"), u = e("../base64"), n = e("../support"), a = e("../external"), o = null;
        if (n.nodestream) try {
          o = e("../nodejs/NodejsStreamOutputAdapter");
        } catch (e2) {
        }
        function l(e2, o2) {
          return new a.Promise(function(t2, r2) {
            var n2 = [], i2 = e2._internalType, s2 = e2._outputType, a2 = e2._mimeType;
            e2.on("data", function(e3, t3) {
              n2.push(e3), o2 && o2(t3);
            }).on("error", function(e3) {
              n2 = [], r2(e3);
            }).on("end", function() {
              try {
                var e3 = (function(e4, t3, r3) {
                  switch (e4) {
                    case "blob":
                      return h.newBlob(h.transformTo("arraybuffer", t3), r3);
                    case "base64":
                      return u.encode(t3);
                    default:
                      return h.transformTo(e4, t3);
                  }
                })(s2, (function(e4, t3) {
                  var r3, n3 = 0, i3 = null, s3 = 0;
                  for (r3 = 0; r3 < t3.length; r3++) s3 += t3[r3].length;
                  switch (e4) {
                    case "string":
                      return t3.join("");
                    case "array":
                      return Array.prototype.concat.apply([], t3);
                    case "uint8array":
                      for (i3 = new Uint8Array(s3), r3 = 0; r3 < t3.length; r3++) i3.set(t3[r3], n3), n3 += t3[r3].length;
                      return i3;
                    case "nodebuffer":
                      return Buffer.concat(t3);
                    default:
                      throw new Error("concat : unsupported type '" + e4 + "'");
                  }
                })(i2, n2), a2);
                t2(e3);
              } catch (e4) {
                r2(e4);
              }
              n2 = [];
            }).resume();
          });
        }
        function f(e2, t2, r2) {
          var n2 = t2;
          switch (t2) {
            case "blob":
            case "arraybuffer":
              n2 = "uint8array";
              break;
            case "base64":
              n2 = "string";
          }
          try {
            this._internalType = n2, this._outputType = t2, this._mimeType = r2, h.checkSupport(n2), this._worker = e2.pipe(new i(n2)), e2.lock();
          } catch (e3) {
            this._worker = new s("error"), this._worker.error(e3);
          }
        }
        f.prototype = { accumulate: function(e2) {
          return l(this, e2);
        }, on: function(e2, t2) {
          var r2 = this;
          return "data" === e2 ? this._worker.on(e2, function(e3) {
            t2.call(r2, e3.data, e3.meta);
          }) : this._worker.on(e2, function() {
            h.delay(t2, arguments, r2);
          }), this;
        }, resume: function() {
          return h.delay(this._worker.resume, [], this._worker), this;
        }, pause: function() {
          return this._worker.pause(), this;
        }, toNodejsStream: function(e2) {
          if (h.checkSupport("nodestream"), "nodebuffer" !== this._outputType) throw new Error(this._outputType + " is not supported by this method");
          return new o(this, { objectMode: "nodebuffer" !== this._outputType }, e2);
        } }, t.exports = f;
      }, { "../base64": 1, "../external": 6, "../nodejs/NodejsStreamOutputAdapter": 13, "../support": 30, "../utils": 32, "./ConvertWorker": 24, "./GenericWorker": 28 }], 30: [function(e, t, r) {
        if (r.base64 = true, r.array = true, r.string = true, r.arraybuffer = "undefined" != typeof ArrayBuffer && "undefined" != typeof Uint8Array, r.nodebuffer = "undefined" != typeof Buffer, r.uint8array = "undefined" != typeof Uint8Array, "undefined" == typeof ArrayBuffer) r.blob = false;
        else {
          var n = new ArrayBuffer(0);
          try {
            r.blob = 0 === new Blob([n], { type: "application/zip" }).size;
          } catch (e2) {
            try {
              var i = new (self.BlobBuilder || self.WebKitBlobBuilder || self.MozBlobBuilder || self.MSBlobBuilder)();
              i.append(n), r.blob = 0 === i.getBlob("application/zip").size;
            } catch (e3) {
              r.blob = false;
            }
          }
        }
        try {
          r.nodestream = !!e("readable-stream").Readable;
        } catch (e2) {
          r.nodestream = false;
        }
      }, { "readable-stream": 16 }], 31: [function(e, t, s) {
        for (var o = e("./utils"), h = e("./support"), r = e("./nodejsUtils"), n = e("./stream/GenericWorker"), u = new Array(256), i = 0; i < 256; i++) u[i] = 252 <= i ? 6 : 248 <= i ? 5 : 240 <= i ? 4 : 224 <= i ? 3 : 192 <= i ? 2 : 1;
        u[254] = u[254] = 1;
        function a() {
          n.call(this, "utf-8 decode"), this.leftOver = null;
        }
        function l() {
          n.call(this, "utf-8 encode");
        }
        s.utf8encode = function(e2) {
          return h.nodebuffer ? r.newBufferFrom(e2, "utf-8") : (function(e3) {
            var t2, r2, n2, i2, s2, a2 = e3.length, o2 = 0;
            for (i2 = 0; i2 < a2; i2++) 55296 == (64512 & (r2 = e3.charCodeAt(i2))) && i2 + 1 < a2 && 56320 == (64512 & (n2 = e3.charCodeAt(i2 + 1))) && (r2 = 65536 + (r2 - 55296 << 10) + (n2 - 56320), i2++), o2 += r2 < 128 ? 1 : r2 < 2048 ? 2 : r2 < 65536 ? 3 : 4;
            for (t2 = h.uint8array ? new Uint8Array(o2) : new Array(o2), i2 = s2 = 0; s2 < o2; i2++) 55296 == (64512 & (r2 = e3.charCodeAt(i2))) && i2 + 1 < a2 && 56320 == (64512 & (n2 = e3.charCodeAt(i2 + 1))) && (r2 = 65536 + (r2 - 55296 << 10) + (n2 - 56320), i2++), r2 < 128 ? t2[s2++] = r2 : (r2 < 2048 ? t2[s2++] = 192 | r2 >>> 6 : (r2 < 65536 ? t2[s2++] = 224 | r2 >>> 12 : (t2[s2++] = 240 | r2 >>> 18, t2[s2++] = 128 | r2 >>> 12 & 63), t2[s2++] = 128 | r2 >>> 6 & 63), t2[s2++] = 128 | 63 & r2);
            return t2;
          })(e2);
        }, s.utf8decode = function(e2) {
          return h.nodebuffer ? o.transformTo("nodebuffer", e2).toString("utf-8") : (function(e3) {
            var t2, r2, n2, i2, s2 = e3.length, a2 = new Array(2 * s2);
            for (t2 = r2 = 0; t2 < s2; ) if ((n2 = e3[t2++]) < 128) a2[r2++] = n2;
            else if (4 < (i2 = u[n2])) a2[r2++] = 65533, t2 += i2 - 1;
            else {
              for (n2 &= 2 === i2 ? 31 : 3 === i2 ? 15 : 7; 1 < i2 && t2 < s2; ) n2 = n2 << 6 | 63 & e3[t2++], i2--;
              1 < i2 ? a2[r2++] = 65533 : n2 < 65536 ? a2[r2++] = n2 : (n2 -= 65536, a2[r2++] = 55296 | n2 >> 10 & 1023, a2[r2++] = 56320 | 1023 & n2);
            }
            return a2.length !== r2 && (a2.subarray ? a2 = a2.subarray(0, r2) : a2.length = r2), o.applyFromCharCode(a2);
          })(e2 = o.transformTo(h.uint8array ? "uint8array" : "array", e2));
        }, o.inherits(a, n), a.prototype.processChunk = function(e2) {
          var t2 = o.transformTo(h.uint8array ? "uint8array" : "array", e2.data);
          if (this.leftOver && this.leftOver.length) {
            if (h.uint8array) {
              var r2 = t2;
              (t2 = new Uint8Array(r2.length + this.leftOver.length)).set(this.leftOver, 0), t2.set(r2, this.leftOver.length);
            } else t2 = this.leftOver.concat(t2);
            this.leftOver = null;
          }
          var n2 = (function(e3, t3) {
            var r3;
            for ((t3 = t3 || e3.length) > e3.length && (t3 = e3.length), r3 = t3 - 1; 0 <= r3 && 128 == (192 & e3[r3]); ) r3--;
            return r3 < 0 ? t3 : 0 === r3 ? t3 : r3 + u[e3[r3]] > t3 ? r3 : t3;
          })(t2), i2 = t2;
          n2 !== t2.length && (h.uint8array ? (i2 = t2.subarray(0, n2), this.leftOver = t2.subarray(n2, t2.length)) : (i2 = t2.slice(0, n2), this.leftOver = t2.slice(n2, t2.length))), this.push({ data: s.utf8decode(i2), meta: e2.meta });
        }, a.prototype.flush = function() {
          this.leftOver && this.leftOver.length && (this.push({ data: s.utf8decode(this.leftOver), meta: {} }), this.leftOver = null);
        }, s.Utf8DecodeWorker = a, o.inherits(l, n), l.prototype.processChunk = function(e2) {
          this.push({ data: s.utf8encode(e2.data), meta: e2.meta });
        }, s.Utf8EncodeWorker = l;
      }, { "./nodejsUtils": 14, "./stream/GenericWorker": 28, "./support": 30, "./utils": 32 }], 32: [function(e, t, a) {
        var o = e("./support"), h = e("./base64"), r = e("./nodejsUtils"), u = e("./external");
        function n(e2) {
          return e2;
        }
        function l(e2, t2) {
          for (var r2 = 0; r2 < e2.length; ++r2) t2[r2] = 255 & e2.charCodeAt(r2);
          return t2;
        }
        e("setimmediate"), a.newBlob = function(t2, r2) {
          a.checkSupport("blob");
          try {
            return new Blob([t2], { type: r2 });
          } catch (e2) {
            try {
              var n2 = new (self.BlobBuilder || self.WebKitBlobBuilder || self.MozBlobBuilder || self.MSBlobBuilder)();
              return n2.append(t2), n2.getBlob(r2);
            } catch (e3) {
              throw new Error("Bug : can't construct the Blob.");
            }
          }
        };
        var i = { stringifyByChunk: function(e2, t2, r2) {
          var n2 = [], i2 = 0, s2 = e2.length;
          if (s2 <= r2) return String.fromCharCode.apply(null, e2);
          for (; i2 < s2; ) "array" === t2 || "nodebuffer" === t2 ? n2.push(String.fromCharCode.apply(null, e2.slice(i2, Math.min(i2 + r2, s2)))) : n2.push(String.fromCharCode.apply(null, e2.subarray(i2, Math.min(i2 + r2, s2)))), i2 += r2;
          return n2.join("");
        }, stringifyByChar: function(e2) {
          for (var t2 = "", r2 = 0; r2 < e2.length; r2++) t2 += String.fromCharCode(e2[r2]);
          return t2;
        }, applyCanBeUsed: { uint8array: (function() {
          try {
            return o.uint8array && 1 === String.fromCharCode.apply(null, new Uint8Array(1)).length;
          } catch (e2) {
            return false;
          }
        })(), nodebuffer: (function() {
          try {
            return o.nodebuffer && 1 === String.fromCharCode.apply(null, r.allocBuffer(1)).length;
          } catch (e2) {
            return false;
          }
        })() } };
        function s(e2) {
          var t2 = 65536, r2 = a.getTypeOf(e2), n2 = true;
          if ("uint8array" === r2 ? n2 = i.applyCanBeUsed.uint8array : "nodebuffer" === r2 && (n2 = i.applyCanBeUsed.nodebuffer), n2) for (; 1 < t2; ) try {
            return i.stringifyByChunk(e2, r2, t2);
          } catch (e3) {
            t2 = Math.floor(t2 / 2);
          }
          return i.stringifyByChar(e2);
        }
        function f(e2, t2) {
          for (var r2 = 0; r2 < e2.length; r2++) t2[r2] = e2[r2];
          return t2;
        }
        a.applyFromCharCode = s;
        var c = {};
        c.string = { string: n, array: function(e2) {
          return l(e2, new Array(e2.length));
        }, arraybuffer: function(e2) {
          return c.string.uint8array(e2).buffer;
        }, uint8array: function(e2) {
          return l(e2, new Uint8Array(e2.length));
        }, nodebuffer: function(e2) {
          return l(e2, r.allocBuffer(e2.length));
        } }, c.array = { string: s, array: n, arraybuffer: function(e2) {
          return new Uint8Array(e2).buffer;
        }, uint8array: function(e2) {
          return new Uint8Array(e2);
        }, nodebuffer: function(e2) {
          return r.newBufferFrom(e2);
        } }, c.arraybuffer = { string: function(e2) {
          return s(new Uint8Array(e2));
        }, array: function(e2) {
          return f(new Uint8Array(e2), new Array(e2.byteLength));
        }, arraybuffer: n, uint8array: function(e2) {
          return new Uint8Array(e2);
        }, nodebuffer: function(e2) {
          return r.newBufferFrom(new Uint8Array(e2));
        } }, c.uint8array = { string: s, array: function(e2) {
          return f(e2, new Array(e2.length));
        }, arraybuffer: function(e2) {
          return e2.buffer;
        }, uint8array: n, nodebuffer: function(e2) {
          return r.newBufferFrom(e2);
        } }, c.nodebuffer = { string: s, array: function(e2) {
          return f(e2, new Array(e2.length));
        }, arraybuffer: function(e2) {
          return c.nodebuffer.uint8array(e2).buffer;
        }, uint8array: function(e2) {
          return f(e2, new Uint8Array(e2.length));
        }, nodebuffer: n }, a.transformTo = function(e2, t2) {
          if (t2 = t2 || "", !e2) return t2;
          a.checkSupport(e2);
          var r2 = a.getTypeOf(t2);
          return c[r2][e2](t2);
        }, a.resolve = function(e2) {
          for (var t2 = e2.split("/"), r2 = [], n2 = 0; n2 < t2.length; n2++) {
            var i2 = t2[n2];
            "." === i2 || "" === i2 && 0 !== n2 && n2 !== t2.length - 1 || (".." === i2 ? r2.pop() : r2.push(i2));
          }
          return r2.join("/");
        }, a.getTypeOf = function(e2) {
          return "string" == typeof e2 ? "string" : "[object Array]" === Object.prototype.toString.call(e2) ? "array" : o.nodebuffer && r.isBuffer(e2) ? "nodebuffer" : o.uint8array && e2 instanceof Uint8Array ? "uint8array" : o.arraybuffer && e2 instanceof ArrayBuffer ? "arraybuffer" : void 0;
        }, a.checkSupport = function(e2) {
          if (!o[e2.toLowerCase()]) throw new Error(e2 + " is not supported by this platform");
        }, a.MAX_VALUE_16BITS = 65535, a.MAX_VALUE_32BITS = -1, a.pretty = function(e2) {
          var t2, r2, n2 = "";
          for (r2 = 0; r2 < (e2 || "").length; r2++) n2 += "\\x" + ((t2 = e2.charCodeAt(r2)) < 16 ? "0" : "") + t2.toString(16).toUpperCase();
          return n2;
        }, a.delay = function(e2, t2, r2) {
          setImmediate(function() {
            e2.apply(r2 || null, t2 || []);
          });
        }, a.inherits = function(e2, t2) {
          function r2() {
          }
          r2.prototype = t2.prototype, e2.prototype = new r2();
        }, a.extend = function() {
          var e2, t2, r2 = {};
          for (e2 = 0; e2 < arguments.length; e2++) for (t2 in arguments[e2]) Object.prototype.hasOwnProperty.call(arguments[e2], t2) && void 0 === r2[t2] && (r2[t2] = arguments[e2][t2]);
          return r2;
        }, a.prepareContent = function(r2, e2, n2, i2, s2) {
          return u.Promise.resolve(e2).then(function(n3) {
            return o.blob && (n3 instanceof Blob || -1 !== ["[object File]", "[object Blob]"].indexOf(Object.prototype.toString.call(n3))) && "undefined" != typeof FileReader ? new u.Promise(function(t2, r3) {
              var e3 = new FileReader();
              e3.onload = function(e4) {
                t2(e4.target.result);
              }, e3.onerror = function(e4) {
                r3(e4.target.error);
              }, e3.readAsArrayBuffer(n3);
            }) : n3;
          }).then(function(e3) {
            var t2 = a.getTypeOf(e3);
            return t2 ? ("arraybuffer" === t2 ? e3 = a.transformTo("uint8array", e3) : "string" === t2 && (s2 ? e3 = h.decode(e3) : n2 && true !== i2 && (e3 = (function(e4) {
              return l(e4, o.uint8array ? new Uint8Array(e4.length) : new Array(e4.length));
            })(e3))), e3) : u.Promise.reject(new Error("Can't read the data of '" + r2 + "'. Is it in a supported JavaScript type (String, Blob, ArrayBuffer, etc) ?"));
          });
        };
      }, { "./base64": 1, "./external": 6, "./nodejsUtils": 14, "./support": 30, setimmediate: 54 }], 33: [function(e, t, r) {
        var n = e("./reader/readerFor"), i = e("./utils"), s = e("./signature"), a = e("./zipEntry"), o = e("./support");
        function h(e2) {
          this.files = [], this.loadOptions = e2;
        }
        h.prototype = { checkSignature: function(e2) {
          if (!this.reader.readAndCheckSignature(e2)) {
            this.reader.index -= 4;
            var t2 = this.reader.readString(4);
            throw new Error("Corrupted zip or bug: unexpected signature (" + i.pretty(t2) + ", expected " + i.pretty(e2) + ")");
          }
        }, isSignature: function(e2, t2) {
          var r2 = this.reader.index;
          this.reader.setIndex(e2);
          var n2 = this.reader.readString(4) === t2;
          return this.reader.setIndex(r2), n2;
        }, readBlockEndOfCentral: function() {
          this.diskNumber = this.reader.readInt(2), this.diskWithCentralDirStart = this.reader.readInt(2), this.centralDirRecordsOnThisDisk = this.reader.readInt(2), this.centralDirRecords = this.reader.readInt(2), this.centralDirSize = this.reader.readInt(4), this.centralDirOffset = this.reader.readInt(4), this.zipCommentLength = this.reader.readInt(2);
          var e2 = this.reader.readData(this.zipCommentLength), t2 = o.uint8array ? "uint8array" : "array", r2 = i.transformTo(t2, e2);
          this.zipComment = this.loadOptions.decodeFileName(r2);
        }, readBlockZip64EndOfCentral: function() {
          this.zip64EndOfCentralSize = this.reader.readInt(8), this.reader.skip(4), this.diskNumber = this.reader.readInt(4), this.diskWithCentralDirStart = this.reader.readInt(4), this.centralDirRecordsOnThisDisk = this.reader.readInt(8), this.centralDirRecords = this.reader.readInt(8), this.centralDirSize = this.reader.readInt(8), this.centralDirOffset = this.reader.readInt(8), this.zip64ExtensibleData = {};
          for (var e2, t2, r2, n2 = this.zip64EndOfCentralSize - 44; 0 < n2; ) e2 = this.reader.readInt(2), t2 = this.reader.readInt(4), r2 = this.reader.readData(t2), this.zip64ExtensibleData[e2] = { id: e2, length: t2, value: r2 };
        }, readBlockZip64EndOfCentralLocator: function() {
          if (this.diskWithZip64CentralDirStart = this.reader.readInt(4), this.relativeOffsetEndOfZip64CentralDir = this.reader.readInt(8), this.disksCount = this.reader.readInt(4), 1 < this.disksCount) throw new Error("Multi-volumes zip are not supported");
        }, readLocalFiles: function() {
          var e2, t2;
          for (e2 = 0; e2 < this.files.length; e2++) t2 = this.files[e2], this.reader.setIndex(t2.localHeaderOffset), this.checkSignature(s.LOCAL_FILE_HEADER), t2.readLocalPart(this.reader), t2.handleUTF8(), t2.processAttributes();
        }, readCentralDir: function() {
          var e2;
          for (this.reader.setIndex(this.centralDirOffset); this.reader.readAndCheckSignature(s.CENTRAL_FILE_HEADER); ) (e2 = new a({ zip64: this.zip64 }, this.loadOptions)).readCentralPart(this.reader), this.files.push(e2);
          if (this.centralDirRecords !== this.files.length && 0 !== this.centralDirRecords && 0 === this.files.length) throw new Error("Corrupted zip or bug: expected " + this.centralDirRecords + " records in central dir, got " + this.files.length);
        }, readEndOfCentral: function() {
          var e2 = this.reader.lastIndexOfSignature(s.CENTRAL_DIRECTORY_END);
          if (e2 < 0) throw !this.isSignature(0, s.LOCAL_FILE_HEADER) ? new Error("Can't find end of central directory : is this a zip file ? If it is, see https://stuk.github.io/jszip/documentation/howto/read_zip.html") : new Error("Corrupted zip: can't find end of central directory");
          this.reader.setIndex(e2);
          var t2 = e2;
          if (this.checkSignature(s.CENTRAL_DIRECTORY_END), this.readBlockEndOfCentral(), this.diskNumber === i.MAX_VALUE_16BITS || this.diskWithCentralDirStart === i.MAX_VALUE_16BITS || this.centralDirRecordsOnThisDisk === i.MAX_VALUE_16BITS || this.centralDirRecords === i.MAX_VALUE_16BITS || this.centralDirSize === i.MAX_VALUE_32BITS || this.centralDirOffset === i.MAX_VALUE_32BITS) {
            if (this.zip64 = true, (e2 = this.reader.lastIndexOfSignature(s.ZIP64_CENTRAL_DIRECTORY_LOCATOR)) < 0) throw new Error("Corrupted zip: can't find the ZIP64 end of central directory locator");
            if (this.reader.setIndex(e2), this.checkSignature(s.ZIP64_CENTRAL_DIRECTORY_LOCATOR), this.readBlockZip64EndOfCentralLocator(), !this.isSignature(this.relativeOffsetEndOfZip64CentralDir, s.ZIP64_CENTRAL_DIRECTORY_END) && (this.relativeOffsetEndOfZip64CentralDir = this.reader.lastIndexOfSignature(s.ZIP64_CENTRAL_DIRECTORY_END), this.relativeOffsetEndOfZip64CentralDir < 0)) throw new Error("Corrupted zip: can't find the ZIP64 end of central directory");
            this.reader.setIndex(this.relativeOffsetEndOfZip64CentralDir), this.checkSignature(s.ZIP64_CENTRAL_DIRECTORY_END), this.readBlockZip64EndOfCentral();
          }
          var r2 = this.centralDirOffset + this.centralDirSize;
          this.zip64 && (r2 += 20, r2 += 12 + this.zip64EndOfCentralSize);
          var n2 = t2 - r2;
          if (0 < n2) this.isSignature(t2, s.CENTRAL_FILE_HEADER) || (this.reader.zero = n2);
          else if (n2 < 0) throw new Error("Corrupted zip: missing " + Math.abs(n2) + " bytes.");
        }, prepareReader: function(e2) {
          this.reader = n(e2);
        }, load: function(e2) {
          this.prepareReader(e2), this.readEndOfCentral(), this.readCentralDir(), this.readLocalFiles();
        } }, t.exports = h;
      }, { "./reader/readerFor": 22, "./signature": 23, "./support": 30, "./utils": 32, "./zipEntry": 34 }], 34: [function(e, t, r) {
        var n = e("./reader/readerFor"), s = e("./utils"), i = e("./compressedObject"), a = e("./crc32"), o = e("./utf8"), h = e("./compressions"), u = e("./support");
        function l(e2, t2) {
          this.options = e2, this.loadOptions = t2;
        }
        l.prototype = { isEncrypted: function() {
          return 1 == (1 & this.bitFlag);
        }, useUTF8: function() {
          return 2048 == (2048 & this.bitFlag);
        }, readLocalPart: function(e2) {
          var t2, r2;
          if (e2.skip(22), this.fileNameLength = e2.readInt(2), r2 = e2.readInt(2), this.fileName = e2.readData(this.fileNameLength), e2.skip(r2), -1 === this.compressedSize || -1 === this.uncompressedSize) throw new Error("Bug or corrupted zip : didn't get enough information from the central directory (compressedSize === -1 || uncompressedSize === -1)");
          if (null === (t2 = (function(e3) {
            for (var t3 in h) if (Object.prototype.hasOwnProperty.call(h, t3) && h[t3].magic === e3) return h[t3];
            return null;
          })(this.compressionMethod))) throw new Error("Corrupted zip : compression " + s.pretty(this.compressionMethod) + " unknown (inner file : " + s.transformTo("string", this.fileName) + ")");
          this.decompressed = new i(this.compressedSize, this.uncompressedSize, this.crc32, t2, e2.readData(this.compressedSize));
        }, readCentralPart: function(e2) {
          this.versionMadeBy = e2.readInt(2), e2.skip(2), this.bitFlag = e2.readInt(2), this.compressionMethod = e2.readString(2), this.date = e2.readDate(), this.crc32 = e2.readInt(4), this.compressedSize = e2.readInt(4), this.uncompressedSize = e2.readInt(4);
          var t2 = e2.readInt(2);
          if (this.extraFieldsLength = e2.readInt(2), this.fileCommentLength = e2.readInt(2), this.diskNumberStart = e2.readInt(2), this.internalFileAttributes = e2.readInt(2), this.externalFileAttributes = e2.readInt(4), this.localHeaderOffset = e2.readInt(4), this.isEncrypted()) throw new Error("Encrypted zip are not supported");
          e2.skip(t2), this.readExtraFields(e2), this.parseZIP64ExtraField(e2), this.fileComment = e2.readData(this.fileCommentLength);
        }, processAttributes: function() {
          this.unixPermissions = null, this.dosPermissions = null;
          var e2 = this.versionMadeBy >> 8;
          this.dir = !!(16 & this.externalFileAttributes), 0 == e2 && (this.dosPermissions = 63 & this.externalFileAttributes), 3 == e2 && (this.unixPermissions = this.externalFileAttributes >> 16 & 65535), this.dir || "/" !== this.fileNameStr.slice(-1) || (this.dir = true);
        }, parseZIP64ExtraField: function() {
          if (this.extraFields[1]) {
            var e2 = n(this.extraFields[1].value);
            this.uncompressedSize === s.MAX_VALUE_32BITS && (this.uncompressedSize = e2.readInt(8)), this.compressedSize === s.MAX_VALUE_32BITS && (this.compressedSize = e2.readInt(8)), this.localHeaderOffset === s.MAX_VALUE_32BITS && (this.localHeaderOffset = e2.readInt(8)), this.diskNumberStart === s.MAX_VALUE_32BITS && (this.diskNumberStart = e2.readInt(4));
          }
        }, readExtraFields: function(e2) {
          var t2, r2, n2, i2 = e2.index + this.extraFieldsLength;
          for (this.extraFields || (this.extraFields = {}); e2.index + 4 < i2; ) t2 = e2.readInt(2), r2 = e2.readInt(2), n2 = e2.readData(r2), this.extraFields[t2] = { id: t2, length: r2, value: n2 };
          e2.setIndex(i2);
        }, handleUTF8: function() {
          var e2 = u.uint8array ? "uint8array" : "array";
          if (this.useUTF8()) this.fileNameStr = o.utf8decode(this.fileName), this.fileCommentStr = o.utf8decode(this.fileComment);
          else {
            var t2 = this.findExtraFieldUnicodePath();
            if (null !== t2) this.fileNameStr = t2;
            else {
              var r2 = s.transformTo(e2, this.fileName);
              this.fileNameStr = this.loadOptions.decodeFileName(r2);
            }
            var n2 = this.findExtraFieldUnicodeComment();
            if (null !== n2) this.fileCommentStr = n2;
            else {
              var i2 = s.transformTo(e2, this.fileComment);
              this.fileCommentStr = this.loadOptions.decodeFileName(i2);
            }
          }
        }, findExtraFieldUnicodePath: function() {
          var e2 = this.extraFields[28789];
          if (e2) {
            var t2 = n(e2.value);
            return 1 !== t2.readInt(1) ? null : a(this.fileName) !== t2.readInt(4) ? null : o.utf8decode(t2.readData(e2.length - 5));
          }
          return null;
        }, findExtraFieldUnicodeComment: function() {
          var e2 = this.extraFields[25461];
          if (e2) {
            var t2 = n(e2.value);
            return 1 !== t2.readInt(1) ? null : a(this.fileComment) !== t2.readInt(4) ? null : o.utf8decode(t2.readData(e2.length - 5));
          }
          return null;
        } }, t.exports = l;
      }, { "./compressedObject": 2, "./compressions": 3, "./crc32": 4, "./reader/readerFor": 22, "./support": 30, "./utf8": 31, "./utils": 32 }], 35: [function(e, t, r) {
        function n(e2, t2, r2) {
          this.name = e2, this.dir = r2.dir, this.date = r2.date, this.comment = r2.comment, this.unixPermissions = r2.unixPermissions, this.dosPermissions = r2.dosPermissions, this._data = t2, this._dataBinary = r2.binary, this.options = { compression: r2.compression, compressionOptions: r2.compressionOptions };
        }
        var s = e("./stream/StreamHelper"), i = e("./stream/DataWorker"), a = e("./utf8"), o = e("./compressedObject"), h = e("./stream/GenericWorker");
        n.prototype = { internalStream: function(e2) {
          var t2 = null, r2 = "string";
          try {
            if (!e2) throw new Error("No output type specified.");
            var n2 = "string" === (r2 = e2.toLowerCase()) || "text" === r2;
            "binarystring" !== r2 && "text" !== r2 || (r2 = "string"), t2 = this._decompressWorker();
            var i2 = !this._dataBinary;
            i2 && !n2 && (t2 = t2.pipe(new a.Utf8EncodeWorker())), !i2 && n2 && (t2 = t2.pipe(new a.Utf8DecodeWorker()));
          } catch (e3) {
            (t2 = new h("error")).error(e3);
          }
          return new s(t2, r2, "");
        }, async: function(e2, t2) {
          return this.internalStream(e2).accumulate(t2);
        }, nodeStream: function(e2, t2) {
          return this.internalStream(e2 || "nodebuffer").toNodejsStream(t2);
        }, _compressWorker: function(e2, t2) {
          if (this._data instanceof o && this._data.compression.magic === e2.magic) return this._data.getCompressedWorker();
          var r2 = this._decompressWorker();
          return this._dataBinary || (r2 = r2.pipe(new a.Utf8EncodeWorker())), o.createWorkerFrom(r2, e2, t2);
        }, _decompressWorker: function() {
          return this._data instanceof o ? this._data.getContentWorker() : this._data instanceof h ? this._data : new i(this._data);
        } };
        for (var u = ["asText", "asBinary", "asNodeBuffer", "asUint8Array", "asArrayBuffer"], l = function() {
          throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.");
        }, f = 0; f < u.length; f++) n.prototype[u[f]] = l;
        t.exports = n;
      }, { "./compressedObject": 2, "./stream/DataWorker": 27, "./stream/GenericWorker": 28, "./stream/StreamHelper": 29, "./utf8": 31 }], 36: [function(e, l, t) {
        (function(t2) {
          var r, n, e2 = t2.MutationObserver || t2.WebKitMutationObserver;
          if (e2) {
            var i = 0, s = new e2(u), a = t2.document.createTextNode("");
            s.observe(a, { characterData: true }), r = function() {
              a.data = i = ++i % 2;
            };
          } else if (t2.setImmediate || void 0 === t2.MessageChannel) r = "document" in t2 && "onreadystatechange" in t2.document.createElement("script") ? function() {
            var e3 = t2.document.createElement("script");
            e3.onreadystatechange = function() {
              u(), e3.onreadystatechange = null, e3.parentNode.removeChild(e3), e3 = null;
            }, t2.document.documentElement.appendChild(e3);
          } : function() {
            setTimeout(u, 0);
          };
          else {
            var o = new t2.MessageChannel();
            o.port1.onmessage = u, r = function() {
              o.port2.postMessage(0);
            };
          }
          var h = [];
          function u() {
            var e3, t3;
            n = true;
            for (var r2 = h.length; r2; ) {
              for (t3 = h, h = [], e3 = -1; ++e3 < r2; ) t3[e3]();
              r2 = h.length;
            }
            n = false;
          }
          l.exports = function(e3) {
            1 !== h.push(e3) || n || r();
          };
        }).call(this, "undefined" != typeof commonjsGlobal ? commonjsGlobal : "undefined" != typeof self ? self : "undefined" != typeof window ? window : {});
      }, {}], 37: [function(e, t, r) {
        var i = e("immediate");
        function u() {
        }
        var l = {}, s = ["REJECTED"], a = ["FULFILLED"], n = ["PENDING"];
        function o(e2) {
          if ("function" != typeof e2) throw new TypeError("resolver must be a function");
          this.state = n, this.queue = [], this.outcome = void 0, e2 !== u && d(this, e2);
        }
        function h(e2, t2, r2) {
          this.promise = e2, "function" == typeof t2 && (this.onFulfilled = t2, this.callFulfilled = this.otherCallFulfilled), "function" == typeof r2 && (this.onRejected = r2, this.callRejected = this.otherCallRejected);
        }
        function f(t2, r2, n2) {
          i(function() {
            var e2;
            try {
              e2 = r2(n2);
            } catch (e3) {
              return l.reject(t2, e3);
            }
            e2 === t2 ? l.reject(t2, new TypeError("Cannot resolve promise with itself")) : l.resolve(t2, e2);
          });
        }
        function c(e2) {
          var t2 = e2 && e2.then;
          if (e2 && ("object" == typeof e2 || "function" == typeof e2) && "function" == typeof t2) return function() {
            t2.apply(e2, arguments);
          };
        }
        function d(t2, e2) {
          var r2 = false;
          function n2(e3) {
            r2 || (r2 = true, l.reject(t2, e3));
          }
          function i2(e3) {
            r2 || (r2 = true, l.resolve(t2, e3));
          }
          var s2 = p(function() {
            e2(i2, n2);
          });
          "error" === s2.status && n2(s2.value);
        }
        function p(e2, t2) {
          var r2 = {};
          try {
            r2.value = e2(t2), r2.status = "success";
          } catch (e3) {
            r2.status = "error", r2.value = e3;
          }
          return r2;
        }
        (t.exports = o).prototype.finally = function(t2) {
          if ("function" != typeof t2) return this;
          var r2 = this.constructor;
          return this.then(function(e2) {
            return r2.resolve(t2()).then(function() {
              return e2;
            });
          }, function(e2) {
            return r2.resolve(t2()).then(function() {
              throw e2;
            });
          });
        }, o.prototype.catch = function(e2) {
          return this.then(null, e2);
        }, o.prototype.then = function(e2, t2) {
          if ("function" != typeof e2 && this.state === a || "function" != typeof t2 && this.state === s) return this;
          var r2 = new this.constructor(u);
          this.state !== n ? f(r2, this.state === a ? e2 : t2, this.outcome) : this.queue.push(new h(r2, e2, t2));
          return r2;
        }, h.prototype.callFulfilled = function(e2) {
          l.resolve(this.promise, e2);
        }, h.prototype.otherCallFulfilled = function(e2) {
          f(this.promise, this.onFulfilled, e2);
        }, h.prototype.callRejected = function(e2) {
          l.reject(this.promise, e2);
        }, h.prototype.otherCallRejected = function(e2) {
          f(this.promise, this.onRejected, e2);
        }, l.resolve = function(e2, t2) {
          var r2 = p(c, t2);
          if ("error" === r2.status) return l.reject(e2, r2.value);
          var n2 = r2.value;
          if (n2) d(e2, n2);
          else {
            e2.state = a, e2.outcome = t2;
            for (var i2 = -1, s2 = e2.queue.length; ++i2 < s2; ) e2.queue[i2].callFulfilled(t2);
          }
          return e2;
        }, l.reject = function(e2, t2) {
          e2.state = s, e2.outcome = t2;
          for (var r2 = -1, n2 = e2.queue.length; ++r2 < n2; ) e2.queue[r2].callRejected(t2);
          return e2;
        }, o.resolve = function(e2) {
          if (e2 instanceof this) return e2;
          return l.resolve(new this(u), e2);
        }, o.reject = function(e2) {
          var t2 = new this(u);
          return l.reject(t2, e2);
        }, o.all = function(e2) {
          var r2 = this;
          if ("[object Array]" !== Object.prototype.toString.call(e2)) return this.reject(new TypeError("must be an array"));
          var n2 = e2.length, i2 = false;
          if (!n2) return this.resolve([]);
          var s2 = new Array(n2), a2 = 0, t2 = -1, o2 = new this(u);
          for (; ++t2 < n2; ) h2(e2[t2], t2);
          return o2;
          function h2(e3, t3) {
            r2.resolve(e3).then(function(e4) {
              s2[t3] = e4, ++a2 !== n2 || i2 || (i2 = true, l.resolve(o2, s2));
            }, function(e4) {
              i2 || (i2 = true, l.reject(o2, e4));
            });
          }
        }, o.race = function(e2) {
          var t2 = this;
          if ("[object Array]" !== Object.prototype.toString.call(e2)) return this.reject(new TypeError("must be an array"));
          var r2 = e2.length, n2 = false;
          if (!r2) return this.resolve([]);
          var i2 = -1, s2 = new this(u);
          for (; ++i2 < r2; ) a2 = e2[i2], t2.resolve(a2).then(function(e3) {
            n2 || (n2 = true, l.resolve(s2, e3));
          }, function(e3) {
            n2 || (n2 = true, l.reject(s2, e3));
          });
          var a2;
          return s2;
        };
      }, { immediate: 36 }], 38: [function(e, t, r) {
        var n = {};
        (0, e("./lib/utils/common").assign)(n, e("./lib/deflate"), e("./lib/inflate"), e("./lib/zlib/constants")), t.exports = n;
      }, { "./lib/deflate": 39, "./lib/inflate": 40, "./lib/utils/common": 41, "./lib/zlib/constants": 44 }], 39: [function(e, t, r) {
        var a = e("./zlib/deflate"), o = e("./utils/common"), h = e("./utils/strings"), i = e("./zlib/messages"), s = e("./zlib/zstream"), u = Object.prototype.toString, l = 0, f = -1, c = 0, d = 8;
        function p(e2) {
          if (!(this instanceof p)) return new p(e2);
          this.options = o.assign({ level: f, method: d, chunkSize: 16384, windowBits: 15, memLevel: 8, strategy: c, to: "" }, e2 || {});
          var t2 = this.options;
          t2.raw && 0 < t2.windowBits ? t2.windowBits = -t2.windowBits : t2.gzip && 0 < t2.windowBits && t2.windowBits < 16 && (t2.windowBits += 16), this.err = 0, this.msg = "", this.ended = false, this.chunks = [], this.strm = new s(), this.strm.avail_out = 0;
          var r2 = a.deflateInit2(this.strm, t2.level, t2.method, t2.windowBits, t2.memLevel, t2.strategy);
          if (r2 !== l) throw new Error(i[r2]);
          if (t2.header && a.deflateSetHeader(this.strm, t2.header), t2.dictionary) {
            var n2;
            if (n2 = "string" == typeof t2.dictionary ? h.string2buf(t2.dictionary) : "[object ArrayBuffer]" === u.call(t2.dictionary) ? new Uint8Array(t2.dictionary) : t2.dictionary, (r2 = a.deflateSetDictionary(this.strm, n2)) !== l) throw new Error(i[r2]);
            this._dict_set = true;
          }
        }
        function n(e2, t2) {
          var r2 = new p(t2);
          if (r2.push(e2, true), r2.err) throw r2.msg || i[r2.err];
          return r2.result;
        }
        p.prototype.push = function(e2, t2) {
          var r2, n2, i2 = this.strm, s2 = this.options.chunkSize;
          if (this.ended) return false;
          n2 = t2 === ~~t2 ? t2 : true === t2 ? 4 : 0, "string" == typeof e2 ? i2.input = h.string2buf(e2) : "[object ArrayBuffer]" === u.call(e2) ? i2.input = new Uint8Array(e2) : i2.input = e2, i2.next_in = 0, i2.avail_in = i2.input.length;
          do {
            if (0 === i2.avail_out && (i2.output = new o.Buf8(s2), i2.next_out = 0, i2.avail_out = s2), 1 !== (r2 = a.deflate(i2, n2)) && r2 !== l) return this.onEnd(r2), !(this.ended = true);
            0 !== i2.avail_out && (0 !== i2.avail_in || 4 !== n2 && 2 !== n2) || ("string" === this.options.to ? this.onData(h.buf2binstring(o.shrinkBuf(i2.output, i2.next_out))) : this.onData(o.shrinkBuf(i2.output, i2.next_out)));
          } while ((0 < i2.avail_in || 0 === i2.avail_out) && 1 !== r2);
          return 4 === n2 ? (r2 = a.deflateEnd(this.strm), this.onEnd(r2), this.ended = true, r2 === l) : 2 !== n2 || (this.onEnd(l), !(i2.avail_out = 0));
        }, p.prototype.onData = function(e2) {
          this.chunks.push(e2);
        }, p.prototype.onEnd = function(e2) {
          e2 === l && ("string" === this.options.to ? this.result = this.chunks.join("") : this.result = o.flattenChunks(this.chunks)), this.chunks = [], this.err = e2, this.msg = this.strm.msg;
        }, r.Deflate = p, r.deflate = n, r.deflateRaw = function(e2, t2) {
          return (t2 = t2 || {}).raw = true, n(e2, t2);
        }, r.gzip = function(e2, t2) {
          return (t2 = t2 || {}).gzip = true, n(e2, t2);
        };
      }, { "./utils/common": 41, "./utils/strings": 42, "./zlib/deflate": 46, "./zlib/messages": 51, "./zlib/zstream": 53 }], 40: [function(e, t, r) {
        var c = e("./zlib/inflate"), d = e("./utils/common"), p = e("./utils/strings"), m = e("./zlib/constants"), n = e("./zlib/messages"), i = e("./zlib/zstream"), s = e("./zlib/gzheader"), _ = Object.prototype.toString;
        function a(e2) {
          if (!(this instanceof a)) return new a(e2);
          this.options = d.assign({ chunkSize: 16384, windowBits: 0, to: "" }, e2 || {});
          var t2 = this.options;
          t2.raw && 0 <= t2.windowBits && t2.windowBits < 16 && (t2.windowBits = -t2.windowBits, 0 === t2.windowBits && (t2.windowBits = -15)), !(0 <= t2.windowBits && t2.windowBits < 16) || e2 && e2.windowBits || (t2.windowBits += 32), 15 < t2.windowBits && t2.windowBits < 48 && 0 == (15 & t2.windowBits) && (t2.windowBits |= 15), this.err = 0, this.msg = "", this.ended = false, this.chunks = [], this.strm = new i(), this.strm.avail_out = 0;
          var r2 = c.inflateInit2(this.strm, t2.windowBits);
          if (r2 !== m.Z_OK) throw new Error(n[r2]);
          this.header = new s(), c.inflateGetHeader(this.strm, this.header);
        }
        function o(e2, t2) {
          var r2 = new a(t2);
          if (r2.push(e2, true), r2.err) throw r2.msg || n[r2.err];
          return r2.result;
        }
        a.prototype.push = function(e2, t2) {
          var r2, n2, i2, s2, a2, o2, h = this.strm, u = this.options.chunkSize, l = this.options.dictionary, f = false;
          if (this.ended) return false;
          n2 = t2 === ~~t2 ? t2 : true === t2 ? m.Z_FINISH : m.Z_NO_FLUSH, "string" == typeof e2 ? h.input = p.binstring2buf(e2) : "[object ArrayBuffer]" === _.call(e2) ? h.input = new Uint8Array(e2) : h.input = e2, h.next_in = 0, h.avail_in = h.input.length;
          do {
            if (0 === h.avail_out && (h.output = new d.Buf8(u), h.next_out = 0, h.avail_out = u), (r2 = c.inflate(h, m.Z_NO_FLUSH)) === m.Z_NEED_DICT && l && (o2 = "string" == typeof l ? p.string2buf(l) : "[object ArrayBuffer]" === _.call(l) ? new Uint8Array(l) : l, r2 = c.inflateSetDictionary(this.strm, o2)), r2 === m.Z_BUF_ERROR && true === f && (r2 = m.Z_OK, f = false), r2 !== m.Z_STREAM_END && r2 !== m.Z_OK) return this.onEnd(r2), !(this.ended = true);
            h.next_out && (0 !== h.avail_out && r2 !== m.Z_STREAM_END && (0 !== h.avail_in || n2 !== m.Z_FINISH && n2 !== m.Z_SYNC_FLUSH) || ("string" === this.options.to ? (i2 = p.utf8border(h.output, h.next_out), s2 = h.next_out - i2, a2 = p.buf2string(h.output, i2), h.next_out = s2, h.avail_out = u - s2, s2 && d.arraySet(h.output, h.output, i2, s2, 0), this.onData(a2)) : this.onData(d.shrinkBuf(h.output, h.next_out)))), 0 === h.avail_in && 0 === h.avail_out && (f = true);
          } while ((0 < h.avail_in || 0 === h.avail_out) && r2 !== m.Z_STREAM_END);
          return r2 === m.Z_STREAM_END && (n2 = m.Z_FINISH), n2 === m.Z_FINISH ? (r2 = c.inflateEnd(this.strm), this.onEnd(r2), this.ended = true, r2 === m.Z_OK) : n2 !== m.Z_SYNC_FLUSH || (this.onEnd(m.Z_OK), !(h.avail_out = 0));
        }, a.prototype.onData = function(e2) {
          this.chunks.push(e2);
        }, a.prototype.onEnd = function(e2) {
          e2 === m.Z_OK && ("string" === this.options.to ? this.result = this.chunks.join("") : this.result = d.flattenChunks(this.chunks)), this.chunks = [], this.err = e2, this.msg = this.strm.msg;
        }, r.Inflate = a, r.inflate = o, r.inflateRaw = function(e2, t2) {
          return (t2 = t2 || {}).raw = true, o(e2, t2);
        }, r.ungzip = o;
      }, { "./utils/common": 41, "./utils/strings": 42, "./zlib/constants": 44, "./zlib/gzheader": 47, "./zlib/inflate": 49, "./zlib/messages": 51, "./zlib/zstream": 53 }], 41: [function(e, t, r) {
        var n = "undefined" != typeof Uint8Array && "undefined" != typeof Uint16Array && "undefined" != typeof Int32Array;
        r.assign = function(e2) {
          for (var t2 = Array.prototype.slice.call(arguments, 1); t2.length; ) {
            var r2 = t2.shift();
            if (r2) {
              if ("object" != typeof r2) throw new TypeError(r2 + "must be non-object");
              for (var n2 in r2) r2.hasOwnProperty(n2) && (e2[n2] = r2[n2]);
            }
          }
          return e2;
        }, r.shrinkBuf = function(e2, t2) {
          return e2.length === t2 ? e2 : e2.subarray ? e2.subarray(0, t2) : (e2.length = t2, e2);
        };
        var i = { arraySet: function(e2, t2, r2, n2, i2) {
          if (t2.subarray && e2.subarray) e2.set(t2.subarray(r2, r2 + n2), i2);
          else for (var s2 = 0; s2 < n2; s2++) e2[i2 + s2] = t2[r2 + s2];
        }, flattenChunks: function(e2) {
          var t2, r2, n2, i2, s2, a;
          for (t2 = n2 = 0, r2 = e2.length; t2 < r2; t2++) n2 += e2[t2].length;
          for (a = new Uint8Array(n2), t2 = i2 = 0, r2 = e2.length; t2 < r2; t2++) s2 = e2[t2], a.set(s2, i2), i2 += s2.length;
          return a;
        } }, s = { arraySet: function(e2, t2, r2, n2, i2) {
          for (var s2 = 0; s2 < n2; s2++) e2[i2 + s2] = t2[r2 + s2];
        }, flattenChunks: function(e2) {
          return [].concat.apply([], e2);
        } };
        r.setTyped = function(e2) {
          e2 ? (r.Buf8 = Uint8Array, r.Buf16 = Uint16Array, r.Buf32 = Int32Array, r.assign(r, i)) : (r.Buf8 = Array, r.Buf16 = Array, r.Buf32 = Array, r.assign(r, s));
        }, r.setTyped(n);
      }, {}], 42: [function(e, t, r) {
        var h = e("./common"), i = true, s = true;
        try {
          String.fromCharCode.apply(null, [0]);
        } catch (e2) {
          i = false;
        }
        try {
          String.fromCharCode.apply(null, new Uint8Array(1));
        } catch (e2) {
          s = false;
        }
        for (var u = new h.Buf8(256), n = 0; n < 256; n++) u[n] = 252 <= n ? 6 : 248 <= n ? 5 : 240 <= n ? 4 : 224 <= n ? 3 : 192 <= n ? 2 : 1;
        function l(e2, t2) {
          if (t2 < 65537 && (e2.subarray && s || !e2.subarray && i)) return String.fromCharCode.apply(null, h.shrinkBuf(e2, t2));
          for (var r2 = "", n2 = 0; n2 < t2; n2++) r2 += String.fromCharCode(e2[n2]);
          return r2;
        }
        u[254] = u[254] = 1, r.string2buf = function(e2) {
          var t2, r2, n2, i2, s2, a = e2.length, o = 0;
          for (i2 = 0; i2 < a; i2++) 55296 == (64512 & (r2 = e2.charCodeAt(i2))) && i2 + 1 < a && 56320 == (64512 & (n2 = e2.charCodeAt(i2 + 1))) && (r2 = 65536 + (r2 - 55296 << 10) + (n2 - 56320), i2++), o += r2 < 128 ? 1 : r2 < 2048 ? 2 : r2 < 65536 ? 3 : 4;
          for (t2 = new h.Buf8(o), i2 = s2 = 0; s2 < o; i2++) 55296 == (64512 & (r2 = e2.charCodeAt(i2))) && i2 + 1 < a && 56320 == (64512 & (n2 = e2.charCodeAt(i2 + 1))) && (r2 = 65536 + (r2 - 55296 << 10) + (n2 - 56320), i2++), r2 < 128 ? t2[s2++] = r2 : (r2 < 2048 ? t2[s2++] = 192 | r2 >>> 6 : (r2 < 65536 ? t2[s2++] = 224 | r2 >>> 12 : (t2[s2++] = 240 | r2 >>> 18, t2[s2++] = 128 | r2 >>> 12 & 63), t2[s2++] = 128 | r2 >>> 6 & 63), t2[s2++] = 128 | 63 & r2);
          return t2;
        }, r.buf2binstring = function(e2) {
          return l(e2, e2.length);
        }, r.binstring2buf = function(e2) {
          for (var t2 = new h.Buf8(e2.length), r2 = 0, n2 = t2.length; r2 < n2; r2++) t2[r2] = e2.charCodeAt(r2);
          return t2;
        }, r.buf2string = function(e2, t2) {
          var r2, n2, i2, s2, a = t2 || e2.length, o = new Array(2 * a);
          for (r2 = n2 = 0; r2 < a; ) if ((i2 = e2[r2++]) < 128) o[n2++] = i2;
          else if (4 < (s2 = u[i2])) o[n2++] = 65533, r2 += s2 - 1;
          else {
            for (i2 &= 2 === s2 ? 31 : 3 === s2 ? 15 : 7; 1 < s2 && r2 < a; ) i2 = i2 << 6 | 63 & e2[r2++], s2--;
            1 < s2 ? o[n2++] = 65533 : i2 < 65536 ? o[n2++] = i2 : (i2 -= 65536, o[n2++] = 55296 | i2 >> 10 & 1023, o[n2++] = 56320 | 1023 & i2);
          }
          return l(o, n2);
        }, r.utf8border = function(e2, t2) {
          var r2;
          for ((t2 = t2 || e2.length) > e2.length && (t2 = e2.length), r2 = t2 - 1; 0 <= r2 && 128 == (192 & e2[r2]); ) r2--;
          return r2 < 0 ? t2 : 0 === r2 ? t2 : r2 + u[e2[r2]] > t2 ? r2 : t2;
        };
      }, { "./common": 41 }], 43: [function(e, t, r) {
        t.exports = function(e2, t2, r2, n) {
          for (var i = 65535 & e2 | 0, s = e2 >>> 16 & 65535 | 0, a = 0; 0 !== r2; ) {
            for (r2 -= a = 2e3 < r2 ? 2e3 : r2; s = s + (i = i + t2[n++] | 0) | 0, --a; ) ;
            i %= 65521, s %= 65521;
          }
          return i | s << 16 | 0;
        };
      }, {}], 44: [function(e, t, r) {
        t.exports = { Z_NO_FLUSH: 0, Z_PARTIAL_FLUSH: 1, Z_SYNC_FLUSH: 2, Z_FULL_FLUSH: 3, Z_FINISH: 4, Z_BLOCK: 5, Z_TREES: 6, Z_OK: 0, Z_STREAM_END: 1, Z_NEED_DICT: 2, Z_ERRNO: -1, Z_STREAM_ERROR: -2, Z_DATA_ERROR: -3, Z_BUF_ERROR: -5, Z_NO_COMPRESSION: 0, Z_BEST_SPEED: 1, Z_BEST_COMPRESSION: 9, Z_DEFAULT_COMPRESSION: -1, Z_FILTERED: 1, Z_HUFFMAN_ONLY: 2, Z_RLE: 3, Z_FIXED: 4, Z_DEFAULT_STRATEGY: 0, Z_BINARY: 0, Z_TEXT: 1, Z_UNKNOWN: 2, Z_DEFLATED: 8 };
      }, {}], 45: [function(e, t, r) {
        var o = (function() {
          for (var e2, t2 = [], r2 = 0; r2 < 256; r2++) {
            e2 = r2;
            for (var n = 0; n < 8; n++) e2 = 1 & e2 ? 3988292384 ^ e2 >>> 1 : e2 >>> 1;
            t2[r2] = e2;
          }
          return t2;
        })();
        t.exports = function(e2, t2, r2, n) {
          var i = o, s = n + r2;
          e2 ^= -1;
          for (var a = n; a < s; a++) e2 = e2 >>> 8 ^ i[255 & (e2 ^ t2[a])];
          return -1 ^ e2;
        };
      }, {}], 46: [function(e, t, r) {
        var h, c = e("../utils/common"), u = e("./trees"), d = e("./adler32"), p = e("./crc32"), n = e("./messages"), l = 0, f = 4, m = 0, _ = -2, g = -1, b = 4, i = 2, v = 8, y = 9, s = 286, a = 30, o = 19, w = 2 * s + 1, k = 15, x = 3, S = 258, z = S + x + 1, C = 42, E = 113, A = 1, I = 2, O = 3, B = 4;
        function R(e2, t2) {
          return e2.msg = n[t2], t2;
        }
        function T(e2) {
          return (e2 << 1) - (4 < e2 ? 9 : 0);
        }
        function D(e2) {
          for (var t2 = e2.length; 0 <= --t2; ) e2[t2] = 0;
        }
        function F(e2) {
          var t2 = e2.state, r2 = t2.pending;
          r2 > e2.avail_out && (r2 = e2.avail_out), 0 !== r2 && (c.arraySet(e2.output, t2.pending_buf, t2.pending_out, r2, e2.next_out), e2.next_out += r2, t2.pending_out += r2, e2.total_out += r2, e2.avail_out -= r2, t2.pending -= r2, 0 === t2.pending && (t2.pending_out = 0));
        }
        function N(e2, t2) {
          u._tr_flush_block(e2, 0 <= e2.block_start ? e2.block_start : -1, e2.strstart - e2.block_start, t2), e2.block_start = e2.strstart, F(e2.strm);
        }
        function U(e2, t2) {
          e2.pending_buf[e2.pending++] = t2;
        }
        function P(e2, t2) {
          e2.pending_buf[e2.pending++] = t2 >>> 8 & 255, e2.pending_buf[e2.pending++] = 255 & t2;
        }
        function L(e2, t2) {
          var r2, n2, i2 = e2.max_chain_length, s2 = e2.strstart, a2 = e2.prev_length, o2 = e2.nice_match, h2 = e2.strstart > e2.w_size - z ? e2.strstart - (e2.w_size - z) : 0, u2 = e2.window, l2 = e2.w_mask, f2 = e2.prev, c2 = e2.strstart + S, d2 = u2[s2 + a2 - 1], p2 = u2[s2 + a2];
          e2.prev_length >= e2.good_match && (i2 >>= 2), o2 > e2.lookahead && (o2 = e2.lookahead);
          do {
            if (u2[(r2 = t2) + a2] === p2 && u2[r2 + a2 - 1] === d2 && u2[r2] === u2[s2] && u2[++r2] === u2[s2 + 1]) {
              s2 += 2, r2++;
              do {
              } while (u2[++s2] === u2[++r2] && u2[++s2] === u2[++r2] && u2[++s2] === u2[++r2] && u2[++s2] === u2[++r2] && u2[++s2] === u2[++r2] && u2[++s2] === u2[++r2] && u2[++s2] === u2[++r2] && u2[++s2] === u2[++r2] && s2 < c2);
              if (n2 = S - (c2 - s2), s2 = c2 - S, a2 < n2) {
                if (e2.match_start = t2, o2 <= (a2 = n2)) break;
                d2 = u2[s2 + a2 - 1], p2 = u2[s2 + a2];
              }
            }
          } while ((t2 = f2[t2 & l2]) > h2 && 0 != --i2);
          return a2 <= e2.lookahead ? a2 : e2.lookahead;
        }
        function j(e2) {
          var t2, r2, n2, i2, s2, a2, o2, h2, u2, l2, f2 = e2.w_size;
          do {
            if (i2 = e2.window_size - e2.lookahead - e2.strstart, e2.strstart >= f2 + (f2 - z)) {
              for (c.arraySet(e2.window, e2.window, f2, f2, 0), e2.match_start -= f2, e2.strstart -= f2, e2.block_start -= f2, t2 = r2 = e2.hash_size; n2 = e2.head[--t2], e2.head[t2] = f2 <= n2 ? n2 - f2 : 0, --r2; ) ;
              for (t2 = r2 = f2; n2 = e2.prev[--t2], e2.prev[t2] = f2 <= n2 ? n2 - f2 : 0, --r2; ) ;
              i2 += f2;
            }
            if (0 === e2.strm.avail_in) break;
            if (a2 = e2.strm, o2 = e2.window, h2 = e2.strstart + e2.lookahead, u2 = i2, l2 = void 0, l2 = a2.avail_in, u2 < l2 && (l2 = u2), r2 = 0 === l2 ? 0 : (a2.avail_in -= l2, c.arraySet(o2, a2.input, a2.next_in, l2, h2), 1 === a2.state.wrap ? a2.adler = d(a2.adler, o2, l2, h2) : 2 === a2.state.wrap && (a2.adler = p(a2.adler, o2, l2, h2)), a2.next_in += l2, a2.total_in += l2, l2), e2.lookahead += r2, e2.lookahead + e2.insert >= x) for (s2 = e2.strstart - e2.insert, e2.ins_h = e2.window[s2], e2.ins_h = (e2.ins_h << e2.hash_shift ^ e2.window[s2 + 1]) & e2.hash_mask; e2.insert && (e2.ins_h = (e2.ins_h << e2.hash_shift ^ e2.window[s2 + x - 1]) & e2.hash_mask, e2.prev[s2 & e2.w_mask] = e2.head[e2.ins_h], e2.head[e2.ins_h] = s2, s2++, e2.insert--, !(e2.lookahead + e2.insert < x)); ) ;
          } while (e2.lookahead < z && 0 !== e2.strm.avail_in);
        }
        function Z(e2, t2) {
          for (var r2, n2; ; ) {
            if (e2.lookahead < z) {
              if (j(e2), e2.lookahead < z && t2 === l) return A;
              if (0 === e2.lookahead) break;
            }
            if (r2 = 0, e2.lookahead >= x && (e2.ins_h = (e2.ins_h << e2.hash_shift ^ e2.window[e2.strstart + x - 1]) & e2.hash_mask, r2 = e2.prev[e2.strstart & e2.w_mask] = e2.head[e2.ins_h], e2.head[e2.ins_h] = e2.strstart), 0 !== r2 && e2.strstart - r2 <= e2.w_size - z && (e2.match_length = L(e2, r2)), e2.match_length >= x) if (n2 = u._tr_tally(e2, e2.strstart - e2.match_start, e2.match_length - x), e2.lookahead -= e2.match_length, e2.match_length <= e2.max_lazy_match && e2.lookahead >= x) {
              for (e2.match_length--; e2.strstart++, e2.ins_h = (e2.ins_h << e2.hash_shift ^ e2.window[e2.strstart + x - 1]) & e2.hash_mask, r2 = e2.prev[e2.strstart & e2.w_mask] = e2.head[e2.ins_h], e2.head[e2.ins_h] = e2.strstart, 0 != --e2.match_length; ) ;
              e2.strstart++;
            } else e2.strstart += e2.match_length, e2.match_length = 0, e2.ins_h = e2.window[e2.strstart], e2.ins_h = (e2.ins_h << e2.hash_shift ^ e2.window[e2.strstart + 1]) & e2.hash_mask;
            else n2 = u._tr_tally(e2, 0, e2.window[e2.strstart]), e2.lookahead--, e2.strstart++;
            if (n2 && (N(e2, false), 0 === e2.strm.avail_out)) return A;
          }
          return e2.insert = e2.strstart < x - 1 ? e2.strstart : x - 1, t2 === f ? (N(e2, true), 0 === e2.strm.avail_out ? O : B) : e2.last_lit && (N(e2, false), 0 === e2.strm.avail_out) ? A : I;
        }
        function W(e2, t2) {
          for (var r2, n2, i2; ; ) {
            if (e2.lookahead < z) {
              if (j(e2), e2.lookahead < z && t2 === l) return A;
              if (0 === e2.lookahead) break;
            }
            if (r2 = 0, e2.lookahead >= x && (e2.ins_h = (e2.ins_h << e2.hash_shift ^ e2.window[e2.strstart + x - 1]) & e2.hash_mask, r2 = e2.prev[e2.strstart & e2.w_mask] = e2.head[e2.ins_h], e2.head[e2.ins_h] = e2.strstart), e2.prev_length = e2.match_length, e2.prev_match = e2.match_start, e2.match_length = x - 1, 0 !== r2 && e2.prev_length < e2.max_lazy_match && e2.strstart - r2 <= e2.w_size - z && (e2.match_length = L(e2, r2), e2.match_length <= 5 && (1 === e2.strategy || e2.match_length === x && 4096 < e2.strstart - e2.match_start) && (e2.match_length = x - 1)), e2.prev_length >= x && e2.match_length <= e2.prev_length) {
              for (i2 = e2.strstart + e2.lookahead - x, n2 = u._tr_tally(e2, e2.strstart - 1 - e2.prev_match, e2.prev_length - x), e2.lookahead -= e2.prev_length - 1, e2.prev_length -= 2; ++e2.strstart <= i2 && (e2.ins_h = (e2.ins_h << e2.hash_shift ^ e2.window[e2.strstart + x - 1]) & e2.hash_mask, r2 = e2.prev[e2.strstart & e2.w_mask] = e2.head[e2.ins_h], e2.head[e2.ins_h] = e2.strstart), 0 != --e2.prev_length; ) ;
              if (e2.match_available = 0, e2.match_length = x - 1, e2.strstart++, n2 && (N(e2, false), 0 === e2.strm.avail_out)) return A;
            } else if (e2.match_available) {
              if ((n2 = u._tr_tally(e2, 0, e2.window[e2.strstart - 1])) && N(e2, false), e2.strstart++, e2.lookahead--, 0 === e2.strm.avail_out) return A;
            } else e2.match_available = 1, e2.strstart++, e2.lookahead--;
          }
          return e2.match_available && (n2 = u._tr_tally(e2, 0, e2.window[e2.strstart - 1]), e2.match_available = 0), e2.insert = e2.strstart < x - 1 ? e2.strstart : x - 1, t2 === f ? (N(e2, true), 0 === e2.strm.avail_out ? O : B) : e2.last_lit && (N(e2, false), 0 === e2.strm.avail_out) ? A : I;
        }
        function M(e2, t2, r2, n2, i2) {
          this.good_length = e2, this.max_lazy = t2, this.nice_length = r2, this.max_chain = n2, this.func = i2;
        }
        function H() {
          this.strm = null, this.status = 0, this.pending_buf = null, this.pending_buf_size = 0, this.pending_out = 0, this.pending = 0, this.wrap = 0, this.gzhead = null, this.gzindex = 0, this.method = v, this.last_flush = -1, this.w_size = 0, this.w_bits = 0, this.w_mask = 0, this.window = null, this.window_size = 0, this.prev = null, this.head = null, this.ins_h = 0, this.hash_size = 0, this.hash_bits = 0, this.hash_mask = 0, this.hash_shift = 0, this.block_start = 0, this.match_length = 0, this.prev_match = 0, this.match_available = 0, this.strstart = 0, this.match_start = 0, this.lookahead = 0, this.prev_length = 0, this.max_chain_length = 0, this.max_lazy_match = 0, this.level = 0, this.strategy = 0, this.good_match = 0, this.nice_match = 0, this.dyn_ltree = new c.Buf16(2 * w), this.dyn_dtree = new c.Buf16(2 * (2 * a + 1)), this.bl_tree = new c.Buf16(2 * (2 * o + 1)), D(this.dyn_ltree), D(this.dyn_dtree), D(this.bl_tree), this.l_desc = null, this.d_desc = null, this.bl_desc = null, this.bl_count = new c.Buf16(k + 1), this.heap = new c.Buf16(2 * s + 1), D(this.heap), this.heap_len = 0, this.heap_max = 0, this.depth = new c.Buf16(2 * s + 1), D(this.depth), this.l_buf = 0, this.lit_bufsize = 0, this.last_lit = 0, this.d_buf = 0, this.opt_len = 0, this.static_len = 0, this.matches = 0, this.insert = 0, this.bi_buf = 0, this.bi_valid = 0;
        }
        function G(e2) {
          var t2;
          return e2 && e2.state ? (e2.total_in = e2.total_out = 0, e2.data_type = i, (t2 = e2.state).pending = 0, t2.pending_out = 0, t2.wrap < 0 && (t2.wrap = -t2.wrap), t2.status = t2.wrap ? C : E, e2.adler = 2 === t2.wrap ? 0 : 1, t2.last_flush = l, u._tr_init(t2), m) : R(e2, _);
        }
        function K(e2) {
          var t2 = G(e2);
          return t2 === m && (function(e3) {
            e3.window_size = 2 * e3.w_size, D(e3.head), e3.max_lazy_match = h[e3.level].max_lazy, e3.good_match = h[e3.level].good_length, e3.nice_match = h[e3.level].nice_length, e3.max_chain_length = h[e3.level].max_chain, e3.strstart = 0, e3.block_start = 0, e3.lookahead = 0, e3.insert = 0, e3.match_length = e3.prev_length = x - 1, e3.match_available = 0, e3.ins_h = 0;
          })(e2.state), t2;
        }
        function Y(e2, t2, r2, n2, i2, s2) {
          if (!e2) return _;
          var a2 = 1;
          if (t2 === g && (t2 = 6), n2 < 0 ? (a2 = 0, n2 = -n2) : 15 < n2 && (a2 = 2, n2 -= 16), i2 < 1 || y < i2 || r2 !== v || n2 < 8 || 15 < n2 || t2 < 0 || 9 < t2 || s2 < 0 || b < s2) return R(e2, _);
          8 === n2 && (n2 = 9);
          var o2 = new H();
          return (e2.state = o2).strm = e2, o2.wrap = a2, o2.gzhead = null, o2.w_bits = n2, o2.w_size = 1 << o2.w_bits, o2.w_mask = o2.w_size - 1, o2.hash_bits = i2 + 7, o2.hash_size = 1 << o2.hash_bits, o2.hash_mask = o2.hash_size - 1, o2.hash_shift = ~~((o2.hash_bits + x - 1) / x), o2.window = new c.Buf8(2 * o2.w_size), o2.head = new c.Buf16(o2.hash_size), o2.prev = new c.Buf16(o2.w_size), o2.lit_bufsize = 1 << i2 + 6, o2.pending_buf_size = 4 * o2.lit_bufsize, o2.pending_buf = new c.Buf8(o2.pending_buf_size), o2.d_buf = 1 * o2.lit_bufsize, o2.l_buf = 3 * o2.lit_bufsize, o2.level = t2, o2.strategy = s2, o2.method = r2, K(e2);
        }
        h = [new M(0, 0, 0, 0, function(e2, t2) {
          var r2 = 65535;
          for (r2 > e2.pending_buf_size - 5 && (r2 = e2.pending_buf_size - 5); ; ) {
            if (e2.lookahead <= 1) {
              if (j(e2), 0 === e2.lookahead && t2 === l) return A;
              if (0 === e2.lookahead) break;
            }
            e2.strstart += e2.lookahead, e2.lookahead = 0;
            var n2 = e2.block_start + r2;
            if ((0 === e2.strstart || e2.strstart >= n2) && (e2.lookahead = e2.strstart - n2, e2.strstart = n2, N(e2, false), 0 === e2.strm.avail_out)) return A;
            if (e2.strstart - e2.block_start >= e2.w_size - z && (N(e2, false), 0 === e2.strm.avail_out)) return A;
          }
          return e2.insert = 0, t2 === f ? (N(e2, true), 0 === e2.strm.avail_out ? O : B) : (e2.strstart > e2.block_start && (N(e2, false), e2.strm.avail_out), A);
        }), new M(4, 4, 8, 4, Z), new M(4, 5, 16, 8, Z), new M(4, 6, 32, 32, Z), new M(4, 4, 16, 16, W), new M(8, 16, 32, 32, W), new M(8, 16, 128, 128, W), new M(8, 32, 128, 256, W), new M(32, 128, 258, 1024, W), new M(32, 258, 258, 4096, W)], r.deflateInit = function(e2, t2) {
          return Y(e2, t2, v, 15, 8, 0);
        }, r.deflateInit2 = Y, r.deflateReset = K, r.deflateResetKeep = G, r.deflateSetHeader = function(e2, t2) {
          return e2 && e2.state ? 2 !== e2.state.wrap ? _ : (e2.state.gzhead = t2, m) : _;
        }, r.deflate = function(e2, t2) {
          var r2, n2, i2, s2;
          if (!e2 || !e2.state || 5 < t2 || t2 < 0) return e2 ? R(e2, _) : _;
          if (n2 = e2.state, !e2.output || !e2.input && 0 !== e2.avail_in || 666 === n2.status && t2 !== f) return R(e2, 0 === e2.avail_out ? -5 : _);
          if (n2.strm = e2, r2 = n2.last_flush, n2.last_flush = t2, n2.status === C) if (2 === n2.wrap) e2.adler = 0, U(n2, 31), U(n2, 139), U(n2, 8), n2.gzhead ? (U(n2, (n2.gzhead.text ? 1 : 0) + (n2.gzhead.hcrc ? 2 : 0) + (n2.gzhead.extra ? 4 : 0) + (n2.gzhead.name ? 8 : 0) + (n2.gzhead.comment ? 16 : 0)), U(n2, 255 & n2.gzhead.time), U(n2, n2.gzhead.time >> 8 & 255), U(n2, n2.gzhead.time >> 16 & 255), U(n2, n2.gzhead.time >> 24 & 255), U(n2, 9 === n2.level ? 2 : 2 <= n2.strategy || n2.level < 2 ? 4 : 0), U(n2, 255 & n2.gzhead.os), n2.gzhead.extra && n2.gzhead.extra.length && (U(n2, 255 & n2.gzhead.extra.length), U(n2, n2.gzhead.extra.length >> 8 & 255)), n2.gzhead.hcrc && (e2.adler = p(e2.adler, n2.pending_buf, n2.pending, 0)), n2.gzindex = 0, n2.status = 69) : (U(n2, 0), U(n2, 0), U(n2, 0), U(n2, 0), U(n2, 0), U(n2, 9 === n2.level ? 2 : 2 <= n2.strategy || n2.level < 2 ? 4 : 0), U(n2, 3), n2.status = E);
          else {
            var a2 = v + (n2.w_bits - 8 << 4) << 8;
            a2 |= (2 <= n2.strategy || n2.level < 2 ? 0 : n2.level < 6 ? 1 : 6 === n2.level ? 2 : 3) << 6, 0 !== n2.strstart && (a2 |= 32), a2 += 31 - a2 % 31, n2.status = E, P(n2, a2), 0 !== n2.strstart && (P(n2, e2.adler >>> 16), P(n2, 65535 & e2.adler)), e2.adler = 1;
          }
          if (69 === n2.status) if (n2.gzhead.extra) {
            for (i2 = n2.pending; n2.gzindex < (65535 & n2.gzhead.extra.length) && (n2.pending !== n2.pending_buf_size || (n2.gzhead.hcrc && n2.pending > i2 && (e2.adler = p(e2.adler, n2.pending_buf, n2.pending - i2, i2)), F(e2), i2 = n2.pending, n2.pending !== n2.pending_buf_size)); ) U(n2, 255 & n2.gzhead.extra[n2.gzindex]), n2.gzindex++;
            n2.gzhead.hcrc && n2.pending > i2 && (e2.adler = p(e2.adler, n2.pending_buf, n2.pending - i2, i2)), n2.gzindex === n2.gzhead.extra.length && (n2.gzindex = 0, n2.status = 73);
          } else n2.status = 73;
          if (73 === n2.status) if (n2.gzhead.name) {
            i2 = n2.pending;
            do {
              if (n2.pending === n2.pending_buf_size && (n2.gzhead.hcrc && n2.pending > i2 && (e2.adler = p(e2.adler, n2.pending_buf, n2.pending - i2, i2)), F(e2), i2 = n2.pending, n2.pending === n2.pending_buf_size)) {
                s2 = 1;
                break;
              }
              s2 = n2.gzindex < n2.gzhead.name.length ? 255 & n2.gzhead.name.charCodeAt(n2.gzindex++) : 0, U(n2, s2);
            } while (0 !== s2);
            n2.gzhead.hcrc && n2.pending > i2 && (e2.adler = p(e2.adler, n2.pending_buf, n2.pending - i2, i2)), 0 === s2 && (n2.gzindex = 0, n2.status = 91);
          } else n2.status = 91;
          if (91 === n2.status) if (n2.gzhead.comment) {
            i2 = n2.pending;
            do {
              if (n2.pending === n2.pending_buf_size && (n2.gzhead.hcrc && n2.pending > i2 && (e2.adler = p(e2.adler, n2.pending_buf, n2.pending - i2, i2)), F(e2), i2 = n2.pending, n2.pending === n2.pending_buf_size)) {
                s2 = 1;
                break;
              }
              s2 = n2.gzindex < n2.gzhead.comment.length ? 255 & n2.gzhead.comment.charCodeAt(n2.gzindex++) : 0, U(n2, s2);
            } while (0 !== s2);
            n2.gzhead.hcrc && n2.pending > i2 && (e2.adler = p(e2.adler, n2.pending_buf, n2.pending - i2, i2)), 0 === s2 && (n2.status = 103);
          } else n2.status = 103;
          if (103 === n2.status && (n2.gzhead.hcrc ? (n2.pending + 2 > n2.pending_buf_size && F(e2), n2.pending + 2 <= n2.pending_buf_size && (U(n2, 255 & e2.adler), U(n2, e2.adler >> 8 & 255), e2.adler = 0, n2.status = E)) : n2.status = E), 0 !== n2.pending) {
            if (F(e2), 0 === e2.avail_out) return n2.last_flush = -1, m;
          } else if (0 === e2.avail_in && T(t2) <= T(r2) && t2 !== f) return R(e2, -5);
          if (666 === n2.status && 0 !== e2.avail_in) return R(e2, -5);
          if (0 !== e2.avail_in || 0 !== n2.lookahead || t2 !== l && 666 !== n2.status) {
            var o2 = 2 === n2.strategy ? (function(e3, t3) {
              for (var r3; ; ) {
                if (0 === e3.lookahead && (j(e3), 0 === e3.lookahead)) {
                  if (t3 === l) return A;
                  break;
                }
                if (e3.match_length = 0, r3 = u._tr_tally(e3, 0, e3.window[e3.strstart]), e3.lookahead--, e3.strstart++, r3 && (N(e3, false), 0 === e3.strm.avail_out)) return A;
              }
              return e3.insert = 0, t3 === f ? (N(e3, true), 0 === e3.strm.avail_out ? O : B) : e3.last_lit && (N(e3, false), 0 === e3.strm.avail_out) ? A : I;
            })(n2, t2) : 3 === n2.strategy ? (function(e3, t3) {
              for (var r3, n3, i3, s3, a3 = e3.window; ; ) {
                if (e3.lookahead <= S) {
                  if (j(e3), e3.lookahead <= S && t3 === l) return A;
                  if (0 === e3.lookahead) break;
                }
                if (e3.match_length = 0, e3.lookahead >= x && 0 < e3.strstart && (n3 = a3[i3 = e3.strstart - 1]) === a3[++i3] && n3 === a3[++i3] && n3 === a3[++i3]) {
                  s3 = e3.strstart + S;
                  do {
                  } while (n3 === a3[++i3] && n3 === a3[++i3] && n3 === a3[++i3] && n3 === a3[++i3] && n3 === a3[++i3] && n3 === a3[++i3] && n3 === a3[++i3] && n3 === a3[++i3] && i3 < s3);
                  e3.match_length = S - (s3 - i3), e3.match_length > e3.lookahead && (e3.match_length = e3.lookahead);
                }
                if (e3.match_length >= x ? (r3 = u._tr_tally(e3, 1, e3.match_length - x), e3.lookahead -= e3.match_length, e3.strstart += e3.match_length, e3.match_length = 0) : (r3 = u._tr_tally(e3, 0, e3.window[e3.strstart]), e3.lookahead--, e3.strstart++), r3 && (N(e3, false), 0 === e3.strm.avail_out)) return A;
              }
              return e3.insert = 0, t3 === f ? (N(e3, true), 0 === e3.strm.avail_out ? O : B) : e3.last_lit && (N(e3, false), 0 === e3.strm.avail_out) ? A : I;
            })(n2, t2) : h[n2.level].func(n2, t2);
            if (o2 !== O && o2 !== B || (n2.status = 666), o2 === A || o2 === O) return 0 === e2.avail_out && (n2.last_flush = -1), m;
            if (o2 === I && (1 === t2 ? u._tr_align(n2) : 5 !== t2 && (u._tr_stored_block(n2, 0, 0, false), 3 === t2 && (D(n2.head), 0 === n2.lookahead && (n2.strstart = 0, n2.block_start = 0, n2.insert = 0))), F(e2), 0 === e2.avail_out)) return n2.last_flush = -1, m;
          }
          return t2 !== f ? m : n2.wrap <= 0 ? 1 : (2 === n2.wrap ? (U(n2, 255 & e2.adler), U(n2, e2.adler >> 8 & 255), U(n2, e2.adler >> 16 & 255), U(n2, e2.adler >> 24 & 255), U(n2, 255 & e2.total_in), U(n2, e2.total_in >> 8 & 255), U(n2, e2.total_in >> 16 & 255), U(n2, e2.total_in >> 24 & 255)) : (P(n2, e2.adler >>> 16), P(n2, 65535 & e2.adler)), F(e2), 0 < n2.wrap && (n2.wrap = -n2.wrap), 0 !== n2.pending ? m : 1);
        }, r.deflateEnd = function(e2) {
          var t2;
          return e2 && e2.state ? (t2 = e2.state.status) !== C && 69 !== t2 && 73 !== t2 && 91 !== t2 && 103 !== t2 && t2 !== E && 666 !== t2 ? R(e2, _) : (e2.state = null, t2 === E ? R(e2, -3) : m) : _;
        }, r.deflateSetDictionary = function(e2, t2) {
          var r2, n2, i2, s2, a2, o2, h2, u2, l2 = t2.length;
          if (!e2 || !e2.state) return _;
          if (2 === (s2 = (r2 = e2.state).wrap) || 1 === s2 && r2.status !== C || r2.lookahead) return _;
          for (1 === s2 && (e2.adler = d(e2.adler, t2, l2, 0)), r2.wrap = 0, l2 >= r2.w_size && (0 === s2 && (D(r2.head), r2.strstart = 0, r2.block_start = 0, r2.insert = 0), u2 = new c.Buf8(r2.w_size), c.arraySet(u2, t2, l2 - r2.w_size, r2.w_size, 0), t2 = u2, l2 = r2.w_size), a2 = e2.avail_in, o2 = e2.next_in, h2 = e2.input, e2.avail_in = l2, e2.next_in = 0, e2.input = t2, j(r2); r2.lookahead >= x; ) {
            for (n2 = r2.strstart, i2 = r2.lookahead - (x - 1); r2.ins_h = (r2.ins_h << r2.hash_shift ^ r2.window[n2 + x - 1]) & r2.hash_mask, r2.prev[n2 & r2.w_mask] = r2.head[r2.ins_h], r2.head[r2.ins_h] = n2, n2++, --i2; ) ;
            r2.strstart = n2, r2.lookahead = x - 1, j(r2);
          }
          return r2.strstart += r2.lookahead, r2.block_start = r2.strstart, r2.insert = r2.lookahead, r2.lookahead = 0, r2.match_length = r2.prev_length = x - 1, r2.match_available = 0, e2.next_in = o2, e2.input = h2, e2.avail_in = a2, r2.wrap = s2, m;
        }, r.deflateInfo = "pako deflate (from Nodeca project)";
      }, { "../utils/common": 41, "./adler32": 43, "./crc32": 45, "./messages": 51, "./trees": 52 }], 47: [function(e, t, r) {
        t.exports = function() {
          this.text = 0, this.time = 0, this.xflags = 0, this.os = 0, this.extra = null, this.extra_len = 0, this.name = "", this.comment = "", this.hcrc = 0, this.done = false;
        };
      }, {}], 48: [function(e, t, r) {
        t.exports = function(e2, t2) {
          var r2, n, i, s, a, o, h, u, l, f, c, d, p, m, _, g, b, v, y, w, k, x, S, z, C;
          r2 = e2.state, n = e2.next_in, z = e2.input, i = n + (e2.avail_in - 5), s = e2.next_out, C = e2.output, a = s - (t2 - e2.avail_out), o = s + (e2.avail_out - 257), h = r2.dmax, u = r2.wsize, l = r2.whave, f = r2.wnext, c = r2.window, d = r2.hold, p = r2.bits, m = r2.lencode, _ = r2.distcode, g = (1 << r2.lenbits) - 1, b = (1 << r2.distbits) - 1;
          e: do {
            p < 15 && (d += z[n++] << p, p += 8, d += z[n++] << p, p += 8), v = m[d & g];
            t: for (; ; ) {
              if (d >>>= y = v >>> 24, p -= y, 0 === (y = v >>> 16 & 255)) C[s++] = 65535 & v;
              else {
                if (!(16 & y)) {
                  if (0 == (64 & y)) {
                    v = m[(65535 & v) + (d & (1 << y) - 1)];
                    continue t;
                  }
                  if (32 & y) {
                    r2.mode = 12;
                    break e;
                  }
                  e2.msg = "invalid literal/length code", r2.mode = 30;
                  break e;
                }
                w = 65535 & v, (y &= 15) && (p < y && (d += z[n++] << p, p += 8), w += d & (1 << y) - 1, d >>>= y, p -= y), p < 15 && (d += z[n++] << p, p += 8, d += z[n++] << p, p += 8), v = _[d & b];
                r: for (; ; ) {
                  if (d >>>= y = v >>> 24, p -= y, !(16 & (y = v >>> 16 & 255))) {
                    if (0 == (64 & y)) {
                      v = _[(65535 & v) + (d & (1 << y) - 1)];
                      continue r;
                    }
                    e2.msg = "invalid distance code", r2.mode = 30;
                    break e;
                  }
                  if (k = 65535 & v, p < (y &= 15) && (d += z[n++] << p, (p += 8) < y && (d += z[n++] << p, p += 8)), h < (k += d & (1 << y) - 1)) {
                    e2.msg = "invalid distance too far back", r2.mode = 30;
                    break e;
                  }
                  if (d >>>= y, p -= y, (y = s - a) < k) {
                    if (l < (y = k - y) && r2.sane) {
                      e2.msg = "invalid distance too far back", r2.mode = 30;
                      break e;
                    }
                    if (S = c, (x = 0) === f) {
                      if (x += u - y, y < w) {
                        for (w -= y; C[s++] = c[x++], --y; ) ;
                        x = s - k, S = C;
                      }
                    } else if (f < y) {
                      if (x += u + f - y, (y -= f) < w) {
                        for (w -= y; C[s++] = c[x++], --y; ) ;
                        if (x = 0, f < w) {
                          for (w -= y = f; C[s++] = c[x++], --y; ) ;
                          x = s - k, S = C;
                        }
                      }
                    } else if (x += f - y, y < w) {
                      for (w -= y; C[s++] = c[x++], --y; ) ;
                      x = s - k, S = C;
                    }
                    for (; 2 < w; ) C[s++] = S[x++], C[s++] = S[x++], C[s++] = S[x++], w -= 3;
                    w && (C[s++] = S[x++], 1 < w && (C[s++] = S[x++]));
                  } else {
                    for (x = s - k; C[s++] = C[x++], C[s++] = C[x++], C[s++] = C[x++], 2 < (w -= 3); ) ;
                    w && (C[s++] = C[x++], 1 < w && (C[s++] = C[x++]));
                  }
                  break;
                }
              }
              break;
            }
          } while (n < i && s < o);
          n -= w = p >> 3, d &= (1 << (p -= w << 3)) - 1, e2.next_in = n, e2.next_out = s, e2.avail_in = n < i ? i - n + 5 : 5 - (n - i), e2.avail_out = s < o ? o - s + 257 : 257 - (s - o), r2.hold = d, r2.bits = p;
        };
      }, {}], 49: [function(e, t, r) {
        var I = e("../utils/common"), O = e("./adler32"), B = e("./crc32"), R = e("./inffast"), T = e("./inftrees"), D = 1, F = 2, N = 0, U = -2, P = 1, n = 852, i = 592;
        function L(e2) {
          return (e2 >>> 24 & 255) + (e2 >>> 8 & 65280) + ((65280 & e2) << 8) + ((255 & e2) << 24);
        }
        function s() {
          this.mode = 0, this.last = false, this.wrap = 0, this.havedict = false, this.flags = 0, this.dmax = 0, this.check = 0, this.total = 0, this.head = null, this.wbits = 0, this.wsize = 0, this.whave = 0, this.wnext = 0, this.window = null, this.hold = 0, this.bits = 0, this.length = 0, this.offset = 0, this.extra = 0, this.lencode = null, this.distcode = null, this.lenbits = 0, this.distbits = 0, this.ncode = 0, this.nlen = 0, this.ndist = 0, this.have = 0, this.next = null, this.lens = new I.Buf16(320), this.work = new I.Buf16(288), this.lendyn = null, this.distdyn = null, this.sane = 0, this.back = 0, this.was = 0;
        }
        function a(e2) {
          var t2;
          return e2 && e2.state ? (t2 = e2.state, e2.total_in = e2.total_out = t2.total = 0, e2.msg = "", t2.wrap && (e2.adler = 1 & t2.wrap), t2.mode = P, t2.last = 0, t2.havedict = 0, t2.dmax = 32768, t2.head = null, t2.hold = 0, t2.bits = 0, t2.lencode = t2.lendyn = new I.Buf32(n), t2.distcode = t2.distdyn = new I.Buf32(i), t2.sane = 1, t2.back = -1, N) : U;
        }
        function o(e2) {
          var t2;
          return e2 && e2.state ? ((t2 = e2.state).wsize = 0, t2.whave = 0, t2.wnext = 0, a(e2)) : U;
        }
        function h(e2, t2) {
          var r2, n2;
          return e2 && e2.state ? (n2 = e2.state, t2 < 0 ? (r2 = 0, t2 = -t2) : (r2 = 1 + (t2 >> 4), t2 < 48 && (t2 &= 15)), t2 && (t2 < 8 || 15 < t2) ? U : (null !== n2.window && n2.wbits !== t2 && (n2.window = null), n2.wrap = r2, n2.wbits = t2, o(e2))) : U;
        }
        function u(e2, t2) {
          var r2, n2;
          return e2 ? (n2 = new s(), (e2.state = n2).window = null, (r2 = h(e2, t2)) !== N && (e2.state = null), r2) : U;
        }
        var l, f, c = true;
        function j(e2) {
          if (c) {
            var t2;
            for (l = new I.Buf32(512), f = new I.Buf32(32), t2 = 0; t2 < 144; ) e2.lens[t2++] = 8;
            for (; t2 < 256; ) e2.lens[t2++] = 9;
            for (; t2 < 280; ) e2.lens[t2++] = 7;
            for (; t2 < 288; ) e2.lens[t2++] = 8;
            for (T(D, e2.lens, 0, 288, l, 0, e2.work, { bits: 9 }), t2 = 0; t2 < 32; ) e2.lens[t2++] = 5;
            T(F, e2.lens, 0, 32, f, 0, e2.work, { bits: 5 }), c = false;
          }
          e2.lencode = l, e2.lenbits = 9, e2.distcode = f, e2.distbits = 5;
        }
        function Z(e2, t2, r2, n2) {
          var i2, s2 = e2.state;
          return null === s2.window && (s2.wsize = 1 << s2.wbits, s2.wnext = 0, s2.whave = 0, s2.window = new I.Buf8(s2.wsize)), n2 >= s2.wsize ? (I.arraySet(s2.window, t2, r2 - s2.wsize, s2.wsize, 0), s2.wnext = 0, s2.whave = s2.wsize) : (n2 < (i2 = s2.wsize - s2.wnext) && (i2 = n2), I.arraySet(s2.window, t2, r2 - n2, i2, s2.wnext), (n2 -= i2) ? (I.arraySet(s2.window, t2, r2 - n2, n2, 0), s2.wnext = n2, s2.whave = s2.wsize) : (s2.wnext += i2, s2.wnext === s2.wsize && (s2.wnext = 0), s2.whave < s2.wsize && (s2.whave += i2))), 0;
        }
        r.inflateReset = o, r.inflateReset2 = h, r.inflateResetKeep = a, r.inflateInit = function(e2) {
          return u(e2, 15);
        }, r.inflateInit2 = u, r.inflate = function(e2, t2) {
          var r2, n2, i2, s2, a2, o2, h2, u2, l2, f2, c2, d, p, m, _, g, b, v, y, w, k, x, S, z, C = 0, E = new I.Buf8(4), A = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15];
          if (!e2 || !e2.state || !e2.output || !e2.input && 0 !== e2.avail_in) return U;
          12 === (r2 = e2.state).mode && (r2.mode = 13), a2 = e2.next_out, i2 = e2.output, h2 = e2.avail_out, s2 = e2.next_in, n2 = e2.input, o2 = e2.avail_in, u2 = r2.hold, l2 = r2.bits, f2 = o2, c2 = h2, x = N;
          e: for (; ; ) switch (r2.mode) {
            case P:
              if (0 === r2.wrap) {
                r2.mode = 13;
                break;
              }
              for (; l2 < 16; ) {
                if (0 === o2) break e;
                o2--, u2 += n2[s2++] << l2, l2 += 8;
              }
              if (2 & r2.wrap && 35615 === u2) {
                E[r2.check = 0] = 255 & u2, E[1] = u2 >>> 8 & 255, r2.check = B(r2.check, E, 2, 0), l2 = u2 = 0, r2.mode = 2;
                break;
              }
              if (r2.flags = 0, r2.head && (r2.head.done = false), !(1 & r2.wrap) || (((255 & u2) << 8) + (u2 >> 8)) % 31) {
                e2.msg = "incorrect header check", r2.mode = 30;
                break;
              }
              if (8 != (15 & u2)) {
                e2.msg = "unknown compression method", r2.mode = 30;
                break;
              }
              if (l2 -= 4, k = 8 + (15 & (u2 >>>= 4)), 0 === r2.wbits) r2.wbits = k;
              else if (k > r2.wbits) {
                e2.msg = "invalid window size", r2.mode = 30;
                break;
              }
              r2.dmax = 1 << k, e2.adler = r2.check = 1, r2.mode = 512 & u2 ? 10 : 12, l2 = u2 = 0;
              break;
            case 2:
              for (; l2 < 16; ) {
                if (0 === o2) break e;
                o2--, u2 += n2[s2++] << l2, l2 += 8;
              }
              if (r2.flags = u2, 8 != (255 & r2.flags)) {
                e2.msg = "unknown compression method", r2.mode = 30;
                break;
              }
              if (57344 & r2.flags) {
                e2.msg = "unknown header flags set", r2.mode = 30;
                break;
              }
              r2.head && (r2.head.text = u2 >> 8 & 1), 512 & r2.flags && (E[0] = 255 & u2, E[1] = u2 >>> 8 & 255, r2.check = B(r2.check, E, 2, 0)), l2 = u2 = 0, r2.mode = 3;
            case 3:
              for (; l2 < 32; ) {
                if (0 === o2) break e;
                o2--, u2 += n2[s2++] << l2, l2 += 8;
              }
              r2.head && (r2.head.time = u2), 512 & r2.flags && (E[0] = 255 & u2, E[1] = u2 >>> 8 & 255, E[2] = u2 >>> 16 & 255, E[3] = u2 >>> 24 & 255, r2.check = B(r2.check, E, 4, 0)), l2 = u2 = 0, r2.mode = 4;
            case 4:
              for (; l2 < 16; ) {
                if (0 === o2) break e;
                o2--, u2 += n2[s2++] << l2, l2 += 8;
              }
              r2.head && (r2.head.xflags = 255 & u2, r2.head.os = u2 >> 8), 512 & r2.flags && (E[0] = 255 & u2, E[1] = u2 >>> 8 & 255, r2.check = B(r2.check, E, 2, 0)), l2 = u2 = 0, r2.mode = 5;
            case 5:
              if (1024 & r2.flags) {
                for (; l2 < 16; ) {
                  if (0 === o2) break e;
                  o2--, u2 += n2[s2++] << l2, l2 += 8;
                }
                r2.length = u2, r2.head && (r2.head.extra_len = u2), 512 & r2.flags && (E[0] = 255 & u2, E[1] = u2 >>> 8 & 255, r2.check = B(r2.check, E, 2, 0)), l2 = u2 = 0;
              } else r2.head && (r2.head.extra = null);
              r2.mode = 6;
            case 6:
              if (1024 & r2.flags && (o2 < (d = r2.length) && (d = o2), d && (r2.head && (k = r2.head.extra_len - r2.length, r2.head.extra || (r2.head.extra = new Array(r2.head.extra_len)), I.arraySet(r2.head.extra, n2, s2, d, k)), 512 & r2.flags && (r2.check = B(r2.check, n2, d, s2)), o2 -= d, s2 += d, r2.length -= d), r2.length)) break e;
              r2.length = 0, r2.mode = 7;
            case 7:
              if (2048 & r2.flags) {
                if (0 === o2) break e;
                for (d = 0; k = n2[s2 + d++], r2.head && k && r2.length < 65536 && (r2.head.name += String.fromCharCode(k)), k && d < o2; ) ;
                if (512 & r2.flags && (r2.check = B(r2.check, n2, d, s2)), o2 -= d, s2 += d, k) break e;
              } else r2.head && (r2.head.name = null);
              r2.length = 0, r2.mode = 8;
            case 8:
              if (4096 & r2.flags) {
                if (0 === o2) break e;
                for (d = 0; k = n2[s2 + d++], r2.head && k && r2.length < 65536 && (r2.head.comment += String.fromCharCode(k)), k && d < o2; ) ;
                if (512 & r2.flags && (r2.check = B(r2.check, n2, d, s2)), o2 -= d, s2 += d, k) break e;
              } else r2.head && (r2.head.comment = null);
              r2.mode = 9;
            case 9:
              if (512 & r2.flags) {
                for (; l2 < 16; ) {
                  if (0 === o2) break e;
                  o2--, u2 += n2[s2++] << l2, l2 += 8;
                }
                if (u2 !== (65535 & r2.check)) {
                  e2.msg = "header crc mismatch", r2.mode = 30;
                  break;
                }
                l2 = u2 = 0;
              }
              r2.head && (r2.head.hcrc = r2.flags >> 9 & 1, r2.head.done = true), e2.adler = r2.check = 0, r2.mode = 12;
              break;
            case 10:
              for (; l2 < 32; ) {
                if (0 === o2) break e;
                o2--, u2 += n2[s2++] << l2, l2 += 8;
              }
              e2.adler = r2.check = L(u2), l2 = u2 = 0, r2.mode = 11;
            case 11:
              if (0 === r2.havedict) return e2.next_out = a2, e2.avail_out = h2, e2.next_in = s2, e2.avail_in = o2, r2.hold = u2, r2.bits = l2, 2;
              e2.adler = r2.check = 1, r2.mode = 12;
            case 12:
              if (5 === t2 || 6 === t2) break e;
            case 13:
              if (r2.last) {
                u2 >>>= 7 & l2, l2 -= 7 & l2, r2.mode = 27;
                break;
              }
              for (; l2 < 3; ) {
                if (0 === o2) break e;
                o2--, u2 += n2[s2++] << l2, l2 += 8;
              }
              switch (r2.last = 1 & u2, l2 -= 1, 3 & (u2 >>>= 1)) {
                case 0:
                  r2.mode = 14;
                  break;
                case 1:
                  if (j(r2), r2.mode = 20, 6 !== t2) break;
                  u2 >>>= 2, l2 -= 2;
                  break e;
                case 2:
                  r2.mode = 17;
                  break;
                case 3:
                  e2.msg = "invalid block type", r2.mode = 30;
              }
              u2 >>>= 2, l2 -= 2;
              break;
            case 14:
              for (u2 >>>= 7 & l2, l2 -= 7 & l2; l2 < 32; ) {
                if (0 === o2) break e;
                o2--, u2 += n2[s2++] << l2, l2 += 8;
              }
              if ((65535 & u2) != (u2 >>> 16 ^ 65535)) {
                e2.msg = "invalid stored block lengths", r2.mode = 30;
                break;
              }
              if (r2.length = 65535 & u2, l2 = u2 = 0, r2.mode = 15, 6 === t2) break e;
            case 15:
              r2.mode = 16;
            case 16:
              if (d = r2.length) {
                if (o2 < d && (d = o2), h2 < d && (d = h2), 0 === d) break e;
                I.arraySet(i2, n2, s2, d, a2), o2 -= d, s2 += d, h2 -= d, a2 += d, r2.length -= d;
                break;
              }
              r2.mode = 12;
              break;
            case 17:
              for (; l2 < 14; ) {
                if (0 === o2) break e;
                o2--, u2 += n2[s2++] << l2, l2 += 8;
              }
              if (r2.nlen = 257 + (31 & u2), u2 >>>= 5, l2 -= 5, r2.ndist = 1 + (31 & u2), u2 >>>= 5, l2 -= 5, r2.ncode = 4 + (15 & u2), u2 >>>= 4, l2 -= 4, 286 < r2.nlen || 30 < r2.ndist) {
                e2.msg = "too many length or distance symbols", r2.mode = 30;
                break;
              }
              r2.have = 0, r2.mode = 18;
            case 18:
              for (; r2.have < r2.ncode; ) {
                for (; l2 < 3; ) {
                  if (0 === o2) break e;
                  o2--, u2 += n2[s2++] << l2, l2 += 8;
                }
                r2.lens[A[r2.have++]] = 7 & u2, u2 >>>= 3, l2 -= 3;
              }
              for (; r2.have < 19; ) r2.lens[A[r2.have++]] = 0;
              if (r2.lencode = r2.lendyn, r2.lenbits = 7, S = { bits: r2.lenbits }, x = T(0, r2.lens, 0, 19, r2.lencode, 0, r2.work, S), r2.lenbits = S.bits, x) {
                e2.msg = "invalid code lengths set", r2.mode = 30;
                break;
              }
              r2.have = 0, r2.mode = 19;
            case 19:
              for (; r2.have < r2.nlen + r2.ndist; ) {
                for (; g = (C = r2.lencode[u2 & (1 << r2.lenbits) - 1]) >>> 16 & 255, b = 65535 & C, !((_ = C >>> 24) <= l2); ) {
                  if (0 === o2) break e;
                  o2--, u2 += n2[s2++] << l2, l2 += 8;
                }
                if (b < 16) u2 >>>= _, l2 -= _, r2.lens[r2.have++] = b;
                else {
                  if (16 === b) {
                    for (z = _ + 2; l2 < z; ) {
                      if (0 === o2) break e;
                      o2--, u2 += n2[s2++] << l2, l2 += 8;
                    }
                    if (u2 >>>= _, l2 -= _, 0 === r2.have) {
                      e2.msg = "invalid bit length repeat", r2.mode = 30;
                      break;
                    }
                    k = r2.lens[r2.have - 1], d = 3 + (3 & u2), u2 >>>= 2, l2 -= 2;
                  } else if (17 === b) {
                    for (z = _ + 3; l2 < z; ) {
                      if (0 === o2) break e;
                      o2--, u2 += n2[s2++] << l2, l2 += 8;
                    }
                    l2 -= _, k = 0, d = 3 + (7 & (u2 >>>= _)), u2 >>>= 3, l2 -= 3;
                  } else {
                    for (z = _ + 7; l2 < z; ) {
                      if (0 === o2) break e;
                      o2--, u2 += n2[s2++] << l2, l2 += 8;
                    }
                    l2 -= _, k = 0, d = 11 + (127 & (u2 >>>= _)), u2 >>>= 7, l2 -= 7;
                  }
                  if (r2.have + d > r2.nlen + r2.ndist) {
                    e2.msg = "invalid bit length repeat", r2.mode = 30;
                    break;
                  }
                  for (; d--; ) r2.lens[r2.have++] = k;
                }
              }
              if (30 === r2.mode) break;
              if (0 === r2.lens[256]) {
                e2.msg = "invalid code -- missing end-of-block", r2.mode = 30;
                break;
              }
              if (r2.lenbits = 9, S = { bits: r2.lenbits }, x = T(D, r2.lens, 0, r2.nlen, r2.lencode, 0, r2.work, S), r2.lenbits = S.bits, x) {
                e2.msg = "invalid literal/lengths set", r2.mode = 30;
                break;
              }
              if (r2.distbits = 6, r2.distcode = r2.distdyn, S = { bits: r2.distbits }, x = T(F, r2.lens, r2.nlen, r2.ndist, r2.distcode, 0, r2.work, S), r2.distbits = S.bits, x) {
                e2.msg = "invalid distances set", r2.mode = 30;
                break;
              }
              if (r2.mode = 20, 6 === t2) break e;
            case 20:
              r2.mode = 21;
            case 21:
              if (6 <= o2 && 258 <= h2) {
                e2.next_out = a2, e2.avail_out = h2, e2.next_in = s2, e2.avail_in = o2, r2.hold = u2, r2.bits = l2, R(e2, c2), a2 = e2.next_out, i2 = e2.output, h2 = e2.avail_out, s2 = e2.next_in, n2 = e2.input, o2 = e2.avail_in, u2 = r2.hold, l2 = r2.bits, 12 === r2.mode && (r2.back = -1);
                break;
              }
              for (r2.back = 0; g = (C = r2.lencode[u2 & (1 << r2.lenbits) - 1]) >>> 16 & 255, b = 65535 & C, !((_ = C >>> 24) <= l2); ) {
                if (0 === o2) break e;
                o2--, u2 += n2[s2++] << l2, l2 += 8;
              }
              if (g && 0 == (240 & g)) {
                for (v = _, y = g, w = b; g = (C = r2.lencode[w + ((u2 & (1 << v + y) - 1) >> v)]) >>> 16 & 255, b = 65535 & C, !(v + (_ = C >>> 24) <= l2); ) {
                  if (0 === o2) break e;
                  o2--, u2 += n2[s2++] << l2, l2 += 8;
                }
                u2 >>>= v, l2 -= v, r2.back += v;
              }
              if (u2 >>>= _, l2 -= _, r2.back += _, r2.length = b, 0 === g) {
                r2.mode = 26;
                break;
              }
              if (32 & g) {
                r2.back = -1, r2.mode = 12;
                break;
              }
              if (64 & g) {
                e2.msg = "invalid literal/length code", r2.mode = 30;
                break;
              }
              r2.extra = 15 & g, r2.mode = 22;
            case 22:
              if (r2.extra) {
                for (z = r2.extra; l2 < z; ) {
                  if (0 === o2) break e;
                  o2--, u2 += n2[s2++] << l2, l2 += 8;
                }
                r2.length += u2 & (1 << r2.extra) - 1, u2 >>>= r2.extra, l2 -= r2.extra, r2.back += r2.extra;
              }
              r2.was = r2.length, r2.mode = 23;
            case 23:
              for (; g = (C = r2.distcode[u2 & (1 << r2.distbits) - 1]) >>> 16 & 255, b = 65535 & C, !((_ = C >>> 24) <= l2); ) {
                if (0 === o2) break e;
                o2--, u2 += n2[s2++] << l2, l2 += 8;
              }
              if (0 == (240 & g)) {
                for (v = _, y = g, w = b; g = (C = r2.distcode[w + ((u2 & (1 << v + y) - 1) >> v)]) >>> 16 & 255, b = 65535 & C, !(v + (_ = C >>> 24) <= l2); ) {
                  if (0 === o2) break e;
                  o2--, u2 += n2[s2++] << l2, l2 += 8;
                }
                u2 >>>= v, l2 -= v, r2.back += v;
              }
              if (u2 >>>= _, l2 -= _, r2.back += _, 64 & g) {
                e2.msg = "invalid distance code", r2.mode = 30;
                break;
              }
              r2.offset = b, r2.extra = 15 & g, r2.mode = 24;
            case 24:
              if (r2.extra) {
                for (z = r2.extra; l2 < z; ) {
                  if (0 === o2) break e;
                  o2--, u2 += n2[s2++] << l2, l2 += 8;
                }
                r2.offset += u2 & (1 << r2.extra) - 1, u2 >>>= r2.extra, l2 -= r2.extra, r2.back += r2.extra;
              }
              if (r2.offset > r2.dmax) {
                e2.msg = "invalid distance too far back", r2.mode = 30;
                break;
              }
              r2.mode = 25;
            case 25:
              if (0 === h2) break e;
              if (d = c2 - h2, r2.offset > d) {
                if ((d = r2.offset - d) > r2.whave && r2.sane) {
                  e2.msg = "invalid distance too far back", r2.mode = 30;
                  break;
                }
                p = d > r2.wnext ? (d -= r2.wnext, r2.wsize - d) : r2.wnext - d, d > r2.length && (d = r2.length), m = r2.window;
              } else m = i2, p = a2 - r2.offset, d = r2.length;
              for (h2 < d && (d = h2), h2 -= d, r2.length -= d; i2[a2++] = m[p++], --d; ) ;
              0 === r2.length && (r2.mode = 21);
              break;
            case 26:
              if (0 === h2) break e;
              i2[a2++] = r2.length, h2--, r2.mode = 21;
              break;
            case 27:
              if (r2.wrap) {
                for (; l2 < 32; ) {
                  if (0 === o2) break e;
                  o2--, u2 |= n2[s2++] << l2, l2 += 8;
                }
                if (c2 -= h2, e2.total_out += c2, r2.total += c2, c2 && (e2.adler = r2.check = r2.flags ? B(r2.check, i2, c2, a2 - c2) : O(r2.check, i2, c2, a2 - c2)), c2 = h2, (r2.flags ? u2 : L(u2)) !== r2.check) {
                  e2.msg = "incorrect data check", r2.mode = 30;
                  break;
                }
                l2 = u2 = 0;
              }
              r2.mode = 28;
            case 28:
              if (r2.wrap && r2.flags) {
                for (; l2 < 32; ) {
                  if (0 === o2) break e;
                  o2--, u2 += n2[s2++] << l2, l2 += 8;
                }
                if (u2 !== (4294967295 & r2.total)) {
                  e2.msg = "incorrect length check", r2.mode = 30;
                  break;
                }
                l2 = u2 = 0;
              }
              r2.mode = 29;
            case 29:
              x = 1;
              break e;
            case 30:
              x = -3;
              break e;
            case 31:
              return -4;
            case 32:
            default:
              return U;
          }
          return e2.next_out = a2, e2.avail_out = h2, e2.next_in = s2, e2.avail_in = o2, r2.hold = u2, r2.bits = l2, (r2.wsize || c2 !== e2.avail_out && r2.mode < 30 && (r2.mode < 27 || 4 !== t2)) && Z(e2, e2.output, e2.next_out, c2 - e2.avail_out) ? (r2.mode = 31, -4) : (f2 -= e2.avail_in, c2 -= e2.avail_out, e2.total_in += f2, e2.total_out += c2, r2.total += c2, r2.wrap && c2 && (e2.adler = r2.check = r2.flags ? B(r2.check, i2, c2, e2.next_out - c2) : O(r2.check, i2, c2, e2.next_out - c2)), e2.data_type = r2.bits + (r2.last ? 64 : 0) + (12 === r2.mode ? 128 : 0) + (20 === r2.mode || 15 === r2.mode ? 256 : 0), (0 == f2 && 0 === c2 || 4 === t2) && x === N && (x = -5), x);
        }, r.inflateEnd = function(e2) {
          if (!e2 || !e2.state) return U;
          var t2 = e2.state;
          return t2.window && (t2.window = null), e2.state = null, N;
        }, r.inflateGetHeader = function(e2, t2) {
          var r2;
          return e2 && e2.state ? 0 == (2 & (r2 = e2.state).wrap) ? U : ((r2.head = t2).done = false, N) : U;
        }, r.inflateSetDictionary = function(e2, t2) {
          var r2, n2 = t2.length;
          return e2 && e2.state ? 0 !== (r2 = e2.state).wrap && 11 !== r2.mode ? U : 11 === r2.mode && O(1, t2, n2, 0) !== r2.check ? -3 : Z(e2, t2, n2, n2) ? (r2.mode = 31, -4) : (r2.havedict = 1, N) : U;
        }, r.inflateInfo = "pako inflate (from Nodeca project)";
      }, { "../utils/common": 41, "./adler32": 43, "./crc32": 45, "./inffast": 48, "./inftrees": 50 }], 50: [function(e, t, r) {
        var D = e("../utils/common"), F = [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258, 0, 0], N = [16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 18, 18, 18, 18, 19, 19, 19, 19, 20, 20, 20, 20, 21, 21, 21, 21, 16, 72, 78], U = [1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577, 0, 0], P = [16, 16, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 64, 64];
        t.exports = function(e2, t2, r2, n, i, s, a, o) {
          var h, u, l, f, c, d, p, m, _, g = o.bits, b = 0, v = 0, y = 0, w = 0, k = 0, x = 0, S = 0, z = 0, C = 0, E = 0, A = null, I = 0, O = new D.Buf16(16), B = new D.Buf16(16), R = null, T = 0;
          for (b = 0; b <= 15; b++) O[b] = 0;
          for (v = 0; v < n; v++) O[t2[r2 + v]]++;
          for (k = g, w = 15; 1 <= w && 0 === O[w]; w--) ;
          if (w < k && (k = w), 0 === w) return i[s++] = 20971520, i[s++] = 20971520, o.bits = 1, 0;
          for (y = 1; y < w && 0 === O[y]; y++) ;
          for (k < y && (k = y), b = z = 1; b <= 15; b++) if (z <<= 1, (z -= O[b]) < 0) return -1;
          if (0 < z && (0 === e2 || 1 !== w)) return -1;
          for (B[1] = 0, b = 1; b < 15; b++) B[b + 1] = B[b] + O[b];
          for (v = 0; v < n; v++) 0 !== t2[r2 + v] && (a[B[t2[r2 + v]]++] = v);
          if (d = 0 === e2 ? (A = R = a, 19) : 1 === e2 ? (A = F, I -= 257, R = N, T -= 257, 256) : (A = U, R = P, -1), b = y, c = s, S = v = E = 0, l = -1, f = (C = 1 << (x = k)) - 1, 1 === e2 && 852 < C || 2 === e2 && 592 < C) return 1;
          for (; ; ) {
            for (p = b - S, _ = a[v] < d ? (m = 0, a[v]) : a[v] > d ? (m = R[T + a[v]], A[I + a[v]]) : (m = 96, 0), h = 1 << b - S, y = u = 1 << x; i[c + (E >> S) + (u -= h)] = p << 24 | m << 16 | _ | 0, 0 !== u; ) ;
            for (h = 1 << b - 1; E & h; ) h >>= 1;
            if (0 !== h ? (E &= h - 1, E += h) : E = 0, v++, 0 == --O[b]) {
              if (b === w) break;
              b = t2[r2 + a[v]];
            }
            if (k < b && (E & f) !== l) {
              for (0 === S && (S = k), c += y, z = 1 << (x = b - S); x + S < w && !((z -= O[x + S]) <= 0); ) x++, z <<= 1;
              if (C += 1 << x, 1 === e2 && 852 < C || 2 === e2 && 592 < C) return 1;
              i[l = E & f] = k << 24 | x << 16 | c - s | 0;
            }
          }
          return 0 !== E && (i[c + E] = b - S << 24 | 64 << 16 | 0), o.bits = k, 0;
        };
      }, { "../utils/common": 41 }], 51: [function(e, t, r) {
        t.exports = { 2: "need dictionary", 1: "stream end", 0: "", "-1": "file error", "-2": "stream error", "-3": "data error", "-4": "insufficient memory", "-5": "buffer error", "-6": "incompatible version" };
      }, {}], 52: [function(e, t, r) {
        var i = e("../utils/common"), o = 0, h = 1;
        function n(e2) {
          for (var t2 = e2.length; 0 <= --t2; ) e2[t2] = 0;
        }
        var s = 0, a = 29, u = 256, l = u + 1 + a, f = 30, c = 19, _ = 2 * l + 1, g = 15, d = 16, p = 7, m = 256, b = 16, v = 17, y = 18, w = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0], k = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13], x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 7], S = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15], z = new Array(2 * (l + 2));
        n(z);
        var C = new Array(2 * f);
        n(C);
        var E = new Array(512);
        n(E);
        var A = new Array(256);
        n(A);
        var I = new Array(a);
        n(I);
        var O, B, R, T = new Array(f);
        function D(e2, t2, r2, n2, i2) {
          this.static_tree = e2, this.extra_bits = t2, this.extra_base = r2, this.elems = n2, this.max_length = i2, this.has_stree = e2 && e2.length;
        }
        function F(e2, t2) {
          this.dyn_tree = e2, this.max_code = 0, this.stat_desc = t2;
        }
        function N(e2) {
          return e2 < 256 ? E[e2] : E[256 + (e2 >>> 7)];
        }
        function U(e2, t2) {
          e2.pending_buf[e2.pending++] = 255 & t2, e2.pending_buf[e2.pending++] = t2 >>> 8 & 255;
        }
        function P(e2, t2, r2) {
          e2.bi_valid > d - r2 ? (e2.bi_buf |= t2 << e2.bi_valid & 65535, U(e2, e2.bi_buf), e2.bi_buf = t2 >> d - e2.bi_valid, e2.bi_valid += r2 - d) : (e2.bi_buf |= t2 << e2.bi_valid & 65535, e2.bi_valid += r2);
        }
        function L(e2, t2, r2) {
          P(e2, r2[2 * t2], r2[2 * t2 + 1]);
        }
        function j(e2, t2) {
          for (var r2 = 0; r2 |= 1 & e2, e2 >>>= 1, r2 <<= 1, 0 < --t2; ) ;
          return r2 >>> 1;
        }
        function Z(e2, t2, r2) {
          var n2, i2, s2 = new Array(g + 1), a2 = 0;
          for (n2 = 1; n2 <= g; n2++) s2[n2] = a2 = a2 + r2[n2 - 1] << 1;
          for (i2 = 0; i2 <= t2; i2++) {
            var o2 = e2[2 * i2 + 1];
            0 !== o2 && (e2[2 * i2] = j(s2[o2]++, o2));
          }
        }
        function W(e2) {
          var t2;
          for (t2 = 0; t2 < l; t2++) e2.dyn_ltree[2 * t2] = 0;
          for (t2 = 0; t2 < f; t2++) e2.dyn_dtree[2 * t2] = 0;
          for (t2 = 0; t2 < c; t2++) e2.bl_tree[2 * t2] = 0;
          e2.dyn_ltree[2 * m] = 1, e2.opt_len = e2.static_len = 0, e2.last_lit = e2.matches = 0;
        }
        function M(e2) {
          8 < e2.bi_valid ? U(e2, e2.bi_buf) : 0 < e2.bi_valid && (e2.pending_buf[e2.pending++] = e2.bi_buf), e2.bi_buf = 0, e2.bi_valid = 0;
        }
        function H(e2, t2, r2, n2) {
          var i2 = 2 * t2, s2 = 2 * r2;
          return e2[i2] < e2[s2] || e2[i2] === e2[s2] && n2[t2] <= n2[r2];
        }
        function G(e2, t2, r2) {
          for (var n2 = e2.heap[r2], i2 = r2 << 1; i2 <= e2.heap_len && (i2 < e2.heap_len && H(t2, e2.heap[i2 + 1], e2.heap[i2], e2.depth) && i2++, !H(t2, n2, e2.heap[i2], e2.depth)); ) e2.heap[r2] = e2.heap[i2], r2 = i2, i2 <<= 1;
          e2.heap[r2] = n2;
        }
        function K(e2, t2, r2) {
          var n2, i2, s2, a2, o2 = 0;
          if (0 !== e2.last_lit) for (; n2 = e2.pending_buf[e2.d_buf + 2 * o2] << 8 | e2.pending_buf[e2.d_buf + 2 * o2 + 1], i2 = e2.pending_buf[e2.l_buf + o2], o2++, 0 === n2 ? L(e2, i2, t2) : (L(e2, (s2 = A[i2]) + u + 1, t2), 0 !== (a2 = w[s2]) && P(e2, i2 -= I[s2], a2), L(e2, s2 = N(--n2), r2), 0 !== (a2 = k[s2]) && P(e2, n2 -= T[s2], a2)), o2 < e2.last_lit; ) ;
          L(e2, m, t2);
        }
        function Y(e2, t2) {
          var r2, n2, i2, s2 = t2.dyn_tree, a2 = t2.stat_desc.static_tree, o2 = t2.stat_desc.has_stree, h2 = t2.stat_desc.elems, u2 = -1;
          for (e2.heap_len = 0, e2.heap_max = _, r2 = 0; r2 < h2; r2++) 0 !== s2[2 * r2] ? (e2.heap[++e2.heap_len] = u2 = r2, e2.depth[r2] = 0) : s2[2 * r2 + 1] = 0;
          for (; e2.heap_len < 2; ) s2[2 * (i2 = e2.heap[++e2.heap_len] = u2 < 2 ? ++u2 : 0)] = 1, e2.depth[i2] = 0, e2.opt_len--, o2 && (e2.static_len -= a2[2 * i2 + 1]);
          for (t2.max_code = u2, r2 = e2.heap_len >> 1; 1 <= r2; r2--) G(e2, s2, r2);
          for (i2 = h2; r2 = e2.heap[1], e2.heap[1] = e2.heap[e2.heap_len--], G(e2, s2, 1), n2 = e2.heap[1], e2.heap[--e2.heap_max] = r2, e2.heap[--e2.heap_max] = n2, s2[2 * i2] = s2[2 * r2] + s2[2 * n2], e2.depth[i2] = (e2.depth[r2] >= e2.depth[n2] ? e2.depth[r2] : e2.depth[n2]) + 1, s2[2 * r2 + 1] = s2[2 * n2 + 1] = i2, e2.heap[1] = i2++, G(e2, s2, 1), 2 <= e2.heap_len; ) ;
          e2.heap[--e2.heap_max] = e2.heap[1], (function(e3, t3) {
            var r3, n3, i3, s3, a3, o3, h3 = t3.dyn_tree, u3 = t3.max_code, l2 = t3.stat_desc.static_tree, f2 = t3.stat_desc.has_stree, c2 = t3.stat_desc.extra_bits, d2 = t3.stat_desc.extra_base, p2 = t3.stat_desc.max_length, m2 = 0;
            for (s3 = 0; s3 <= g; s3++) e3.bl_count[s3] = 0;
            for (h3[2 * e3.heap[e3.heap_max] + 1] = 0, r3 = e3.heap_max + 1; r3 < _; r3++) p2 < (s3 = h3[2 * h3[2 * (n3 = e3.heap[r3]) + 1] + 1] + 1) && (s3 = p2, m2++), h3[2 * n3 + 1] = s3, u3 < n3 || (e3.bl_count[s3]++, a3 = 0, d2 <= n3 && (a3 = c2[n3 - d2]), o3 = h3[2 * n3], e3.opt_len += o3 * (s3 + a3), f2 && (e3.static_len += o3 * (l2[2 * n3 + 1] + a3)));
            if (0 !== m2) {
              do {
                for (s3 = p2 - 1; 0 === e3.bl_count[s3]; ) s3--;
                e3.bl_count[s3]--, e3.bl_count[s3 + 1] += 2, e3.bl_count[p2]--, m2 -= 2;
              } while (0 < m2);
              for (s3 = p2; 0 !== s3; s3--) for (n3 = e3.bl_count[s3]; 0 !== n3; ) u3 < (i3 = e3.heap[--r3]) || (h3[2 * i3 + 1] !== s3 && (e3.opt_len += (s3 - h3[2 * i3 + 1]) * h3[2 * i3], h3[2 * i3 + 1] = s3), n3--);
            }
          })(e2, t2), Z(s2, u2, e2.bl_count);
        }
        function X2(e2, t2, r2) {
          var n2, i2, s2 = -1, a2 = t2[1], o2 = 0, h2 = 7, u2 = 4;
          for (0 === a2 && (h2 = 138, u2 = 3), t2[2 * (r2 + 1) + 1] = 65535, n2 = 0; n2 <= r2; n2++) i2 = a2, a2 = t2[2 * (n2 + 1) + 1], ++o2 < h2 && i2 === a2 || (o2 < u2 ? e2.bl_tree[2 * i2] += o2 : 0 !== i2 ? (i2 !== s2 && e2.bl_tree[2 * i2]++, e2.bl_tree[2 * b]++) : o2 <= 10 ? e2.bl_tree[2 * v]++ : e2.bl_tree[2 * y]++, s2 = i2, u2 = (o2 = 0) === a2 ? (h2 = 138, 3) : i2 === a2 ? (h2 = 6, 3) : (h2 = 7, 4));
        }
        function V(e2, t2, r2) {
          var n2, i2, s2 = -1, a2 = t2[1], o2 = 0, h2 = 7, u2 = 4;
          for (0 === a2 && (h2 = 138, u2 = 3), n2 = 0; n2 <= r2; n2++) if (i2 = a2, a2 = t2[2 * (n2 + 1) + 1], !(++o2 < h2 && i2 === a2)) {
            if (o2 < u2) for (; L(e2, i2, e2.bl_tree), 0 != --o2; ) ;
            else 0 !== i2 ? (i2 !== s2 && (L(e2, i2, e2.bl_tree), o2--), L(e2, b, e2.bl_tree), P(e2, o2 - 3, 2)) : o2 <= 10 ? (L(e2, v, e2.bl_tree), P(e2, o2 - 3, 3)) : (L(e2, y, e2.bl_tree), P(e2, o2 - 11, 7));
            s2 = i2, u2 = (o2 = 0) === a2 ? (h2 = 138, 3) : i2 === a2 ? (h2 = 6, 3) : (h2 = 7, 4);
          }
        }
        n(T);
        var q = false;
        function J(e2, t2, r2, n2) {
          P(e2, (s << 1) + (n2 ? 1 : 0), 3), (function(e3, t3, r3, n3) {
            M(e3), U(e3, r3), U(e3, ~r3), i.arraySet(e3.pending_buf, e3.window, t3, r3, e3.pending), e3.pending += r3;
          })(e2, t2, r2);
        }
        r._tr_init = function(e2) {
          q || ((function() {
            var e3, t2, r2, n2, i2, s2 = new Array(g + 1);
            for (n2 = r2 = 0; n2 < a - 1; n2++) for (I[n2] = r2, e3 = 0; e3 < 1 << w[n2]; e3++) A[r2++] = n2;
            for (A[r2 - 1] = n2, n2 = i2 = 0; n2 < 16; n2++) for (T[n2] = i2, e3 = 0; e3 < 1 << k[n2]; e3++) E[i2++] = n2;
            for (i2 >>= 7; n2 < f; n2++) for (T[n2] = i2 << 7, e3 = 0; e3 < 1 << k[n2] - 7; e3++) E[256 + i2++] = n2;
            for (t2 = 0; t2 <= g; t2++) s2[t2] = 0;
            for (e3 = 0; e3 <= 143; ) z[2 * e3 + 1] = 8, e3++, s2[8]++;
            for (; e3 <= 255; ) z[2 * e3 + 1] = 9, e3++, s2[9]++;
            for (; e3 <= 279; ) z[2 * e3 + 1] = 7, e3++, s2[7]++;
            for (; e3 <= 287; ) z[2 * e3 + 1] = 8, e3++, s2[8]++;
            for (Z(z, l + 1, s2), e3 = 0; e3 < f; e3++) C[2 * e3 + 1] = 5, C[2 * e3] = j(e3, 5);
            O = new D(z, w, u + 1, l, g), B = new D(C, k, 0, f, g), R = new D(new Array(0), x, 0, c, p);
          })(), q = true), e2.l_desc = new F(e2.dyn_ltree, O), e2.d_desc = new F(e2.dyn_dtree, B), e2.bl_desc = new F(e2.bl_tree, R), e2.bi_buf = 0, e2.bi_valid = 0, W(e2);
        }, r._tr_stored_block = J, r._tr_flush_block = function(e2, t2, r2, n2) {
          var i2, s2, a2 = 0;
          0 < e2.level ? (2 === e2.strm.data_type && (e2.strm.data_type = (function(e3) {
            var t3, r3 = 4093624447;
            for (t3 = 0; t3 <= 31; t3++, r3 >>>= 1) if (1 & r3 && 0 !== e3.dyn_ltree[2 * t3]) return o;
            if (0 !== e3.dyn_ltree[18] || 0 !== e3.dyn_ltree[20] || 0 !== e3.dyn_ltree[26]) return h;
            for (t3 = 32; t3 < u; t3++) if (0 !== e3.dyn_ltree[2 * t3]) return h;
            return o;
          })(e2)), Y(e2, e2.l_desc), Y(e2, e2.d_desc), a2 = (function(e3) {
            var t3;
            for (X2(e3, e3.dyn_ltree, e3.l_desc.max_code), X2(e3, e3.dyn_dtree, e3.d_desc.max_code), Y(e3, e3.bl_desc), t3 = c - 1; 3 <= t3 && 0 === e3.bl_tree[2 * S[t3] + 1]; t3--) ;
            return e3.opt_len += 3 * (t3 + 1) + 5 + 5 + 4, t3;
          })(e2), i2 = e2.opt_len + 3 + 7 >>> 3, (s2 = e2.static_len + 3 + 7 >>> 3) <= i2 && (i2 = s2)) : i2 = s2 = r2 + 5, r2 + 4 <= i2 && -1 !== t2 ? J(e2, t2, r2, n2) : 4 === e2.strategy || s2 === i2 ? (P(e2, 2 + (n2 ? 1 : 0), 3), K(e2, z, C)) : (P(e2, 4 + (n2 ? 1 : 0), 3), (function(e3, t3, r3, n3) {
            var i3;
            for (P(e3, t3 - 257, 5), P(e3, r3 - 1, 5), P(e3, n3 - 4, 4), i3 = 0; i3 < n3; i3++) P(e3, e3.bl_tree[2 * S[i3] + 1], 3);
            V(e3, e3.dyn_ltree, t3 - 1), V(e3, e3.dyn_dtree, r3 - 1);
          })(e2, e2.l_desc.max_code + 1, e2.d_desc.max_code + 1, a2 + 1), K(e2, e2.dyn_ltree, e2.dyn_dtree)), W(e2), n2 && M(e2);
        }, r._tr_tally = function(e2, t2, r2) {
          return e2.pending_buf[e2.d_buf + 2 * e2.last_lit] = t2 >>> 8 & 255, e2.pending_buf[e2.d_buf + 2 * e2.last_lit + 1] = 255 & t2, e2.pending_buf[e2.l_buf + e2.last_lit] = 255 & r2, e2.last_lit++, 0 === t2 ? e2.dyn_ltree[2 * r2]++ : (e2.matches++, t2--, e2.dyn_ltree[2 * (A[r2] + u + 1)]++, e2.dyn_dtree[2 * N(t2)]++), e2.last_lit === e2.lit_bufsize - 1;
        }, r._tr_align = function(e2) {
          P(e2, 2, 3), L(e2, m, z), (function(e3) {
            16 === e3.bi_valid ? (U(e3, e3.bi_buf), e3.bi_buf = 0, e3.bi_valid = 0) : 8 <= e3.bi_valid && (e3.pending_buf[e3.pending++] = 255 & e3.bi_buf, e3.bi_buf >>= 8, e3.bi_valid -= 8);
          })(e2);
        };
      }, { "../utils/common": 41 }], 53: [function(e, t, r) {
        t.exports = function() {
          this.input = null, this.next_in = 0, this.avail_in = 0, this.total_in = 0, this.output = null, this.next_out = 0, this.avail_out = 0, this.total_out = 0, this.msg = "", this.state = null, this.data_type = 2, this.adler = 0;
        };
      }, {}], 54: [function(e, t, r) {
        (function(e2) {
          !(function(r2, n) {
            if (!r2.setImmediate) {
              var i, s, t2, a, o = 1, h = {}, u = false, l = r2.document, e3 = Object.getPrototypeOf && Object.getPrototypeOf(r2);
              e3 = e3 && e3.setTimeout ? e3 : r2, i = "[object process]" === {}.toString.call(r2.process) ? function(e4) {
                process.nextTick(function() {
                  c(e4);
                });
              } : (function() {
                if (r2.postMessage && !r2.importScripts) {
                  var e4 = true, t3 = r2.onmessage;
                  return r2.onmessage = function() {
                    e4 = false;
                  }, r2.postMessage("", "*"), r2.onmessage = t3, e4;
                }
              })() ? (a = "setImmediate$" + Math.random() + "$", r2.addEventListener ? r2.addEventListener("message", d, false) : r2.attachEvent("onmessage", d), function(e4) {
                r2.postMessage(a + e4, "*");
              }) : r2.MessageChannel ? ((t2 = new MessageChannel()).port1.onmessage = function(e4) {
                c(e4.data);
              }, function(e4) {
                t2.port2.postMessage(e4);
              }) : l && "onreadystatechange" in l.createElement("script") ? (s = l.documentElement, function(e4) {
                var t3 = l.createElement("script");
                t3.onreadystatechange = function() {
                  c(e4), t3.onreadystatechange = null, s.removeChild(t3), t3 = null;
                }, s.appendChild(t3);
              }) : function(e4) {
                setTimeout(c, 0, e4);
              }, e3.setImmediate = function(e4) {
                "function" != typeof e4 && (e4 = new Function("" + e4));
                for (var t3 = new Array(arguments.length - 1), r3 = 0; r3 < t3.length; r3++) t3[r3] = arguments[r3 + 1];
                var n2 = { callback: e4, args: t3 };
                return h[o] = n2, i(o), o++;
              }, e3.clearImmediate = f;
            }
            function f(e4) {
              delete h[e4];
            }
            function c(e4) {
              if (u) setTimeout(c, 0, e4);
              else {
                var t3 = h[e4];
                if (t3) {
                  u = true;
                  try {
                    !(function(e5) {
                      var t4 = e5.callback, r3 = e5.args;
                      switch (r3.length) {
                        case 0:
                          t4();
                          break;
                        case 1:
                          t4(r3[0]);
                          break;
                        case 2:
                          t4(r3[0], r3[1]);
                          break;
                        case 3:
                          t4(r3[0], r3[1], r3[2]);
                          break;
                        default:
                          t4.apply(n, r3);
                      }
                    })(t3);
                  } finally {
                    f(e4), u = false;
                  }
                }
              }
            }
            function d(e4) {
              e4.source === r2 && "string" == typeof e4.data && 0 === e4.data.indexOf(a) && c(+e4.data.slice(a.length));
            }
          })("undefined" == typeof self ? void 0 === e2 ? this : e2 : self);
        }).call(this, "undefined" != typeof commonjsGlobal ? commonjsGlobal : "undefined" != typeof self ? self : "undefined" != typeof window ? window : {});
      }, {}] }, {}, [10])(10);
    });
  })(jszip_min);
  return jszip_min.exports;
}
var jszip_minExports = requireJszip_min();
const JSZip = /* @__PURE__ */ getDefaultExportFromCjs(jszip_minExports);
async function getSequences() {
  const response = await apiClient.get("/sequences");
  return extractData(response);
}
async function getSequence(name) {
  const response = await apiClient.get(`/sequences/${name}`);
  return extractData(response);
}
async function validateSequence(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post(
    "/sequences/validate",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    }
  );
  return extractData(response);
}
async function uploadSequence(file, force = false, onProgress) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post(
    `/sequences/upload?force=${force}`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data"
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            progressEvent.loaded * 100 / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      }
    }
  );
  return extractData(response);
}
async function filesToZip(files) {
  const zip = new JSZip();
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    if (!file) continue;
    const relativePath = file.webkitRelativePath || file.name;
    if (relativePath.includes("__pycache__") || relativePath.endsWith(".pyc")) {
      continue;
    }
    const content = await file.arrayBuffer();
    zip.file(relativePath, content);
  }
  return zip.generateAsync({ type: "blob", compression: "DEFLATE" });
}
async function uploadSequenceFolder(files, force = false, onProgress) {
  var _a;
  const zipBlob = await filesToZip(files);
  const firstFile = files[0];
  const folderName = ((_a = firstFile == null ? void 0 : firstFile.webkitRelativePath) == null ? void 0 : _a.split("/")[0]) || "sequence";
  const zipFile = new File([zipBlob], `${folderName}.zip`, { type: "application/zip" });
  return uploadSequence(zipFile, force, onProgress);
}
async function deleteSequence(name) {
  await apiClient.delete(`/sequences/${name}`);
}
async function downloadSequence(name) {
  const response = await apiClient.get(`/sequences/${name}/download`, {
    responseType: "blob"
  });
  return response.data;
}
async function runSimulation(sequenceName, mode, parameters) {
  const response = await apiClient.post(
    `/deploy/simulate/${sequenceName}`,
    { mode, parameters }
  );
  return extractData(response);
}
function useSequenceList() {
  return useQuery({
    queryKey: queryKeys.sequences,
    queryFn: getSequences,
    staleTime: 5 * 60 * 1e3
    // 5 minutes - sequences don't change often
  });
}
function useSequence(name) {
  return useQuery({
    queryKey: queryKeys.sequence(name ?? ""),
    queryFn: () => getSequence(name),
    enabled: !!name
  });
}
function useValidateSequence() {
  return useMutation({
    mutationFn: (file) => validateSequence(file)
  });
}
function useUploadSequence() {
  const queryClient2 = useQueryClient();
  const [progress, setProgress] = reactExports.useState({
    stage: "idle",
    progress: 0,
    message: ""
  });
  const resetProgress = reactExports.useCallback(() => {
    setProgress({ stage: "idle", progress: 0, message: "" });
  }, []);
  const mutation = useMutation({
    mutationFn: async ({ file, force }) => {
      var _a;
      setProgress({ stage: "validating", progress: 0, message: "Validating package..." });
      const validation = await validateSequence(file);
      if (!validation.valid) {
        throw new Error(((_a = validation.errors) == null ? void 0 : _a.map((e) => e.message).join(", ")) || "Validation failed");
      }
      setProgress({ stage: "uploading", progress: 0, message: "Uploading package..." });
      const result = await uploadSequence(file, force ?? false, (uploadProgress) => {
        setProgress({
          stage: "uploading",
          progress: uploadProgress,
          message: `Uploading... ${uploadProgress}%`
        });
      });
      setProgress({
        stage: "complete",
        progress: 100,
        message: `Successfully installed ${result.name} v${result.version}`
      });
      return { result, validation };
    },
    onSuccess: async () => {
      await queryClient2.refetchQueries({ queryKey: queryKeys.sequences });
    },
    onError: (error) => {
      setProgress({
        stage: "error",
        progress: 0,
        message: "Upload failed",
        error: error.message
      });
    }
  });
  return {
    ...mutation,
    progress,
    resetProgress
  };
}
function useUploadSequenceFolder() {
  const queryClient2 = useQueryClient();
  const [progress, setProgress] = reactExports.useState({
    stage: "idle",
    progress: 0,
    message: ""
  });
  const resetProgress = reactExports.useCallback(() => {
    setProgress({ stage: "idle", progress: 0, message: "" });
  }, []);
  const mutation = useMutation({
    mutationFn: async ({ files, force }) => {
      setProgress({ stage: "validating", progress: 0, message: "Compressing folder to ZIP..." });
      const result = await uploadSequenceFolder(files, force ?? false, (uploadProgress) => {
        setProgress({
          stage: "uploading",
          progress: uploadProgress,
          message: `Uploading... ${uploadProgress}%`
        });
      });
      setProgress({
        stage: "complete",
        progress: 100,
        message: `Successfully installed ${result.name} v${result.version}`
      });
      return result;
    },
    onSuccess: async () => {
      await queryClient2.refetchQueries({ queryKey: queryKeys.sequences });
    },
    onError: (error) => {
      setProgress({
        stage: "error",
        progress: 0,
        message: "Upload failed",
        error: error.message
      });
    }
  });
  return {
    ...mutation,
    progress,
    resetProgress
  };
}
function useDeleteSequence() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (name) => deleteSequence(name),
    onSuccess: () => {
      queryClient2.invalidateQueries({ queryKey: queryKeys.sequences });
    }
  });
}
function useDownloadSequence() {
  return useMutation({
    mutationFn: async (name) => {
      const blob = await downloadSequence(name);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${name}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      return { name };
    }
  });
}
function useSimulation() {
  return useMutation({
    mutationFn: ({
      sequenceName,
      mode,
      parameters
    }) => runSimulation(sequenceName, mode, parameters)
  });
}
async function getLogs(params) {
  const response = await apiClient.get("/logs", {
    params
  });
  return response.data.data;
}
function useLogList(params) {
  return useQuery({
    queryKey: queryKeys.logs(params),
    queryFn: () => getLogs(params),
    enabled: params !== void 0
  });
}
function snakeToCamel(str) {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}
function transformKeys(obj, options) {
  if (obj === null || obj === void 0) {
    return obj;
  }
  if (obj instanceof Blob || obj instanceof ArrayBuffer || obj instanceof FormData) {
    return obj;
  }
  if (Array.isArray(obj)) {
    return obj.map((item) => transformKeys(item));
  }
  if (typeof obj === "object" && obj.constructor === Object) {
    const transformed = {};
    for (const [key, value] of Object.entries(obj)) {
      const newKey = snakeToCamel(key);
      transformed[newKey] = transformKeys(value);
    }
    return transformed;
  }
  return obj;
}
const WebSocketContext = reactExports.createContext(null);
function generateLogId() {
  return Date.now() * 1e3 + Math.floor(Math.random() * 1e3);
}
function getWebSocketUrl(path) {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host;
  return `${protocol}//${host}${path}`;
}
function WebSocketProvider({ children, url = "/ws" }) {
  const queryClient2 = useQueryClient();
  const socketRef = reactExports.useRef(null);
  const subscriptionRefCount = reactExports.useRef(/* @__PURE__ */ new Map());
  const justSubscribedBatches = reactExports.useRef(/* @__PURE__ */ new Set());
  const reconnectTimeoutRef = reactExports.useRef(null);
  const reconnectAttemptRef = reactExports.useRef(0);
  const setWebSocketStatus = useConnectionStore((s) => s.setWebSocketStatus);
  const updateHeartbeat = useConnectionStore((s) => s.updateHeartbeat);
  const resetReconnectAttempts = useConnectionStore((s) => s.resetReconnectAttempts);
  const incrementReconnectAttempts = useConnectionStore((s) => s.incrementReconnectAttempts);
  const updateBatchStatus = useBatchStore((s) => s.updateBatchStatus);
  const updateStepProgress = useBatchStore((s) => s.updateStepProgress);
  const setLastRunResult = useBatchStore((s) => s.setLastRunResult);
  const incrementBatchStats = useBatchStore((s) => s.incrementBatchStats);
  const startStep = useBatchStore((s) => s.startStep);
  const completeStep = useBatchStore((s) => s.completeStep);
  const clearSteps = useBatchStore((s) => s.clearSteps);
  const addLog = useLogStore((s) => s.addLog);
  const addNotification = useNotificationStore((s) => s.addNotification);
  const handleMessage = reactExports.useCallback(
    (message) => {
      var _a, _b, _c, _d, _e;
      const batchIdForLog = "batchId" in message ? wsLogger.truncateId(message.batchId) : null;
      wsLogger.debug(`Received: ${message.type}`, batchIdForLog ? `batch: ${batchIdForLog}` : "");
      switch (message.type) {
        case "batch_status": {
          const isInitialPush = justSubscribedBatches.current.has(message.batchId);
          if (isInitialPush) {
            justSubscribedBatches.current.delete(message.batchId);
          }
          wsLogger.debug(`batch_status: status=${message.data.status}, step=${message.data.currentStep}, progress=${message.data.progress}, exec=${message.data.executionId}, initial=${isInitialPush}`);
          if (message.data.status === "running" && message.data.progress === 0) {
            clearSteps(message.batchId);
          }
          updateBatchStatus(message.batchId, message.data.status, message.data.executionId, void 0, isInitialPush);
          if (message.data.currentStep !== void 0) {
            updateStepProgress(
              message.batchId,
              message.data.currentStep,
              message.data.stepIndex,
              message.data.progress,
              message.data.executionId
            );
          }
          break;
        }
        case "step_start": {
          wsLogger.debug(`step_start: step=${message.data.step}, index=${message.data.index}/${message.data.total}, exec=${message.data.executionId}`);
          startStep(
            message.batchId,
            message.data.step,
            message.data.index,
            message.data.total,
            message.data.executionId
          );
          updateBatchStatus(message.batchId, "running", message.data.executionId);
          break;
        }
        case "step_complete": {
          wsLogger.debug(`step_complete: step=${message.data.step}, index=${message.data.index}, pass=${message.data.pass}, duration=${message.data.duration}`);
          completeStep(
            message.batchId,
            message.data.step,
            message.data.index,
            message.data.duration,
            message.data.pass,
            message.data.result,
            message.data.executionId
          );
          addLog({
            id: generateLogId(),
            batchId: message.batchId,
            level: message.data.pass ? "info" : "warning",
            message: `Step "${message.data.step}" ${message.data.pass ? "passed" : "failed"} (${message.data.duration.toFixed(2)}s)`,
            timestamp: /* @__PURE__ */ new Date()
          });
          if (!message.data.pass) {
            addNotification({
              type: "warning",
              title: "Step Failed",
              message: `Step "${message.data.step}" failed in batch ${message.batchId.slice(0, 8)}...`,
              batchId: message.batchId
            });
          }
          break;
        }
        case "sequence_complete": {
          updateBatchStatus(message.batchId, "completed", message.data.executionId, message.data.duration);
          setLastRunResult(message.batchId, message.data.overallPass);
          incrementBatchStats(message.batchId, message.data.overallPass);
          addLog({
            id: generateLogId(),
            batchId: message.batchId,
            level: message.data.overallPass ? "info" : "error",
            message: `Sequence ${message.data.overallPass ? "PASSED" : "FAILED"} (${message.data.duration.toFixed(2)}s)`,
            timestamp: /* @__PURE__ */ new Date()
          });
          addNotification({
            type: message.data.overallPass ? "success" : "error",
            title: message.data.overallPass ? "Sequence Passed" : "Sequence Failed",
            message: `Batch ${message.batchId.slice(0, 8)}... completed ${message.data.overallPass ? "successfully" : "with errors"} in ${message.data.duration.toFixed(2)}s`,
            batchId: message.batchId
          });
          queryClient2.invalidateQueries({ queryKey: queryKeys.allBatchStatistics });
          queryClient2.invalidateQueries({ queryKey: queryKeys.batchStatistics(message.batchId) });
          break;
        }
        case "log": {
          addLog({
            id: generateLogId(),
            batchId: message.batchId,
            level: message.data.level,
            message: message.data.message,
            timestamp: new Date(message.data.timestamp)
          });
          break;
        }
        case "error": {
          const code = ((_a = message.data) == null ? void 0 : _a.code) || "UNKNOWN";
          const errorMessage = ((_b = message.data) == null ? void 0 : _b.message) || "Unknown error";
          const step = (_c = message.data) == null ? void 0 : _c.step;
          const timestamp = (_d = message.data) == null ? void 0 : _d.timestamp;
          wsLogger.debug(`error: code=${code}, message=${errorMessage}, step=${step}`);
          toast.error(`[${code}] ${errorMessage}`);
          addLog({
            id: generateLogId(),
            batchId: message.batchId,
            level: "error",
            message: `[${code}] ${errorMessage}${step ? ` (step: ${step})` : ""}`,
            timestamp: timestamp ? new Date(timestamp) : /* @__PURE__ */ new Date()
          });
          addNotification({
            type: "error",
            title: `Error: ${code}`,
            message: errorMessage,
            batchId: message.batchId
          });
          break;
        }
        case "subscribed": {
          const subscribedBatchIds = ((_e = message.data) == null ? void 0 : _e.batchIds) || [];
          for (const batchId of subscribedBatchIds) {
            justSubscribedBatches.current.add(batchId);
          }
          wsLogger.debug(`subscribed: ${subscribedBatchIds.length} batches marked for initial push`);
          break;
        }
        case "unsubscribed":
          break;
        case "batch_created": {
          queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
          addNotification({
            type: "info",
            title: "Batch Created",
            message: `New batch "${message.data.name}" has been created`
          });
          break;
        }
        case "batch_deleted": {
          queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
          addNotification({
            type: "info",
            title: "Batch Deleted",
            message: `Batch has been deleted`,
            batchId: message.batchId
          });
          break;
        }
      }
    },
    [updateBatchStatus, updateStepProgress, setLastRunResult, incrementBatchStats, startStep, completeStep, clearSteps, addLog, addNotification, queryClient2]
  );
  const connect = reactExports.useCallback(() => {
    var _a;
    if (((_a = socketRef.current) == null ? void 0 : _a.readyState) === WebSocket.OPEN) {
      return;
    }
    setWebSocketStatus("connecting");
    const wsUrl = getWebSocketUrl(url);
    const socket = new WebSocket(wsUrl);
    socket.onopen = () => {
      setWebSocketStatus("connected");
      resetReconnectAttempts();
      reconnectAttemptRef.current = 0;
      updateHeartbeat();
      const subscribedBatchIds = Array.from(subscriptionRefCount.current.keys());
      if (subscribedBatchIds.length > 0) {
        wsLogger.debug(`Re-subscribing on connect:`, subscribedBatchIds.map((id) => wsLogger.truncateId(id)));
        const message = {
          type: "subscribe",
          batchIds: subscribedBatchIds
        };
        socket.send(JSON.stringify(message));
      } else {
        wsLogger.debug("Connected, no batches to re-subscribe");
      }
    };
    socket.onmessage = (event) => {
      updateHeartbeat();
      try {
        const rawData = JSON.parse(event.data);
        const data = transformKeys(rawData);
        handleMessage(data);
      } catch (e) {
        wsLogger.error("Failed to parse/handle WebSocket message:", e, "raw:", event.data);
      }
    };
    socket.onclose = () => {
      setWebSocketStatus("disconnected");
      socketRef.current = null;
      const delay = Math.min(
        WEBSOCKET_CONFIG.reconnectionDelay * Math.pow(2, reconnectAttemptRef.current),
        WEBSOCKET_CONFIG.reconnectionDelayMax
      );
      reconnectAttemptRef.current++;
      incrementReconnectAttempts();
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, delay);
    };
    socket.onerror = () => {
      setWebSocketStatus("error");
    };
    socketRef.current = socket;
  }, [
    url,
    setWebSocketStatus,
    resetReconnectAttempts,
    incrementReconnectAttempts,
    updateHeartbeat,
    handleMessage
  ]);
  reactExports.useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [connect]);
  const subscribe = reactExports.useCallback((batchIds) => {
    var _a, _b, _c;
    batchIds.forEach((id) => {
      const currentCount = subscriptionRefCount.current.get(id) || 0;
      subscriptionRefCount.current.set(id, currentCount + 1);
      wsLogger.debug(`subscribe: ${wsLogger.truncateId(id)} refCount: ${currentCount} -> ${currentCount + 1}`);
    });
    if (batchIds.length > 0 && ((_a = socketRef.current) == null ? void 0 : _a.readyState) === WebSocket.OPEN) {
      wsLogger.debug("Sending subscribe for batches:", batchIds.map((id) => wsLogger.truncateId(id)));
      const message = {
        type: "subscribe",
        batchIds
      };
      socketRef.current.send(JSON.stringify(message));
    } else if (((_b = socketRef.current) == null ? void 0 : _b.readyState) !== WebSocket.OPEN) {
      wsLogger.warn(`WebSocket not open (state: ${(_c = socketRef.current) == null ? void 0 : _c.readyState}), subscribe queued for reconnect`);
    }
  }, []);
  const unsubscribe = reactExports.useCallback((batchIds) => {
    var _a;
    const actualUnsubscribes = [];
    batchIds.forEach((id) => {
      const currentCount = subscriptionRefCount.current.get(id) || 0;
      wsLogger.debug(`unsubscribe: ${wsLogger.truncateId(id)} refCount: ${currentCount} -> ${currentCount > 0 ? currentCount - 1 : 0}`);
      if (currentCount > 1) {
        subscriptionRefCount.current.set(id, currentCount - 1);
      } else if (currentCount === 1) {
        subscriptionRefCount.current.delete(id);
        actualUnsubscribes.push(id);
      }
    });
    if (actualUnsubscribes.length > 0 && ((_a = socketRef.current) == null ? void 0 : _a.readyState) === WebSocket.OPEN) {
      wsLogger.debug("Sending unsubscribe for:", actualUnsubscribes.map((id) => wsLogger.truncateId(id)));
      const message = {
        type: "unsubscribe",
        batchIds: actualUnsubscribes
      };
      socketRef.current.send(JSON.stringify(message));
    }
  }, []);
  const send = reactExports.useCallback((message) => {
    var _a;
    if (((_a = socketRef.current) == null ? void 0 : _a.readyState) === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    }
  }, []);
  const isConnected = useConnectionStore((state) => state.websocketStatus === "connected");
  const value = reactExports.useMemo(
    () => ({
      isConnected,
      subscribe,
      unsubscribe,
      send
    }),
    [isConnected, subscribe, unsubscribe, send]
  );
  return /* @__PURE__ */ jsxRuntimeExports.jsx(WebSocketContext.Provider, { value, children });
}
function useWebSocket() {
  const context = reactExports.useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocket must be used within a WebSocketProvider");
  }
  return context;
}
const FALLBACK_ACTIVATION_DELAY = 5e3;
function usePollingFallback() {
  const queryClient2 = useQueryClient();
  const websocketStatus = useConnectionStore((s) => s.websocketStatus);
  const pollingFallbackActive = useConnectionStore((s) => s.pollingFallbackActive);
  const setPollingFallbackActive = useConnectionStore((s) => s.setPollingFallbackActive);
  const activationTimeoutRef = reactExports.useRef(null);
  const wasConnectedRef = reactExports.useRef(false);
  reactExports.useEffect(() => {
    const isConnected = websocketStatus === "connected";
    if (activationTimeoutRef.current) {
      clearTimeout(activationTimeoutRef.current);
      activationTimeoutRef.current = null;
    }
    if (isConnected) {
      if (pollingFallbackActive) {
        setPollingFallbackActive(false);
        void queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
      }
      wasConnectedRef.current = true;
    } else if (wasConnectedRef.current) {
      activationTimeoutRef.current = setTimeout(() => {
        if (!pollingFallbackActive) {
          setPollingFallbackActive(true);
        }
      }, FALLBACK_ACTIVATION_DELAY);
    }
    return () => {
      if (activationTimeoutRef.current) {
        clearTimeout(activationTimeoutRef.current);
      }
    };
  }, [websocketStatus, pollingFallbackActive, setPollingFallbackActive, queryClient2]);
  return {
    isActive: pollingFallbackActive,
    pollingInterval: pollingFallbackActive ? POLLING_INTERVALS.batchesFallback : POLLING_INTERVALS.batches
  };
}
async function getHardwareCommands(batchId, hardwareId) {
  const response = await apiClient.get(
    `/manual/batches/${batchId}/hardware/${hardwareId}/commands`
  );
  return extractData(response);
}
async function getManualSteps(batchId) {
  const response = await apiClient.get(
    `/manual/batches/${batchId}/sequence/steps`
  );
  return extractData(response);
}
async function runManualStep(batchId, stepName, parameters) {
  const response = await apiClient.post(
    `/manual/batches/${batchId}/sequence/steps/${stepName}/run`,
    parameters ? { parameters } : void 0
  );
  return extractData(response);
}
async function skipManualStep(batchId, stepName) {
  const response = await apiClient.post(
    `/manual/batches/${batchId}/sequence/steps/${stepName}/skip`
  );
  return extractData(response);
}
async function resetManualSequence(batchId) {
  await apiClient.post(`/manual/batches/${batchId}/sequence/reset`);
}
const MAX_HISTORY_SIZE = 50;
function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
}
const useManualControlStore = create((set) => ({
  // Device selection
  selectedBatchId: null,
  selectedHardwareId: null,
  // Command state
  selectedCommand: null,
  parameterValues: {},
  // Results
  resultHistory: [],
  // Presets
  presets: [],
  // Manual sequence mode
  manualSequenceMode: false,
  sequenceSteps: [],
  currentStepIndex: 0,
  stepOverrides: {},
  // Actions
  selectDevice: (batchId, hardwareId) => {
    set({
      selectedBatchId: batchId,
      selectedHardwareId: hardwareId,
      selectedCommand: null,
      parameterValues: {}
    });
  },
  selectCommand: (command) => {
    const parameterValues = {};
    if (command) {
      command.parameters.forEach((param) => {
        if (param.default !== void 0) {
          parameterValues[param.name] = param.default;
        }
      });
    }
    set({ selectedCommand: command, parameterValues });
  },
  setParameterValue: (name, value) => {
    set((state) => ({
      parameterValues: {
        ...state.parameterValues,
        [name]: value
      }
    }));
  },
  setParameterValues: (values) => {
    set({ parameterValues: values });
  },
  addResultToHistory: (entry) => {
    const newEntry = {
      ...entry,
      id: generateId(),
      timestamp: /* @__PURE__ */ new Date()
    };
    set((state) => ({
      resultHistory: [newEntry, ...state.resultHistory].slice(0, MAX_HISTORY_SIZE)
    }));
  },
  clearHistory: () => {
    set({ resultHistory: [] });
  },
  addPreset: (preset) => {
    set((state) => ({
      presets: [...state.presets, preset]
    }));
  },
  removePreset: (presetId) => {
    set((state) => ({
      presets: state.presets.filter((p) => p.id !== presetId)
    }));
  },
  // Manual sequence actions
  setManualSequenceMode: (enabled) => {
    set({ manualSequenceMode: enabled });
  },
  setSequenceSteps: (steps) => {
    set({
      sequenceSteps: steps,
      currentStepIndex: 0,
      stepOverrides: {}
    });
  },
  updateStepStatus: (stepName, status, result, duration) => {
    set((state) => ({
      sequenceSteps: state.sequenceSteps.map(
        (step) => step.name === stepName ? { ...step, status, result, duration } : step
      )
    }));
  },
  setCurrentStepIndex: (index) => {
    set({ currentStepIndex: index });
  },
  setStepOverride: (stepName, overrides) => {
    set((state) => ({
      stepOverrides: {
        ...state.stepOverrides,
        [stepName]: overrides
      }
    }));
  },
  resetSequence: () => {
    set((state) => ({
      sequenceSteps: state.sequenceSteps.map((step) => ({
        ...step,
        status: "pending",
        result: void 0,
        duration: void 0
      })),
      currentStepIndex: 0
    }));
  }
}));
const selectGroupedCommands = (commands) => {
  const grouped = {
    measurement: [],
    control: [],
    configuration: [],
    diagnostic: []
  };
  commands.forEach((cmd) => {
    const category = cmd.category;
    if (grouped[category]) {
      grouped[category].push(cmd);
    }
  });
  return grouped;
};
const manualQueryKeys = {
  hardware: (batchId) => ["manual", "hardware", batchId],
  commands: (batchId, hardwareId) => ["manual", "commands", batchId, hardwareId],
  steps: (batchId) => ["manual", "steps", batchId],
  presets: () => ["manual", "presets"]
};
function useHardwareCommands(batchId, hardwareId) {
  return useQuery({
    queryKey: manualQueryKeys.commands(batchId ?? "", hardwareId ?? ""),
    queryFn: () => getHardwareCommands(batchId, hardwareId),
    enabled: !!batchId && !!hardwareId,
    staleTime: 60 * 1e3
    // 1 minute - commands don't change often
  });
}
function useManualSteps(batchId) {
  const setSequenceSteps = useManualControlStore(
    (state) => state.setSequenceSteps
  );
  const query = useQuery({
    queryKey: manualQueryKeys.steps(batchId ?? ""),
    queryFn: () => getManualSteps(batchId),
    enabled: !!batchId,
    staleTime: 30 * 1e3
    // 30 seconds
  });
  if (query.data) {
    setSequenceSteps(query.data);
  }
  return query;
}
function useExecuteCommand() {
  const addResultToHistory = useManualControlStore(
    (state) => state.addResultToHistory
  );
  return useMutation({
    mutationFn: async ({
      batchId,
      request,
      command
    }) => {
      const startTime = Date.now();
      const response = await manualControl(batchId, request);
      const duration = Date.now() - startTime;
      return { response, duration, command };
    },
    onSuccess: ({ response, duration, command }, { request }) => {
      addResultToHistory({
        hardware: request.hardware,
        command: request.command,
        params: request.params ?? {},
        result: response.result,
        success: true,
        duration,
        unit: command == null ? void 0 : command.returnUnit
      });
      toast.success("Command executed successfully");
    },
    onError: (error, { request }) => {
      addResultToHistory({
        hardware: request.hardware,
        command: request.command,
        params: request.params ?? {},
        result: { error: getErrorMessage(error) },
        success: false,
        duration: 0
      });
      toast.error(`Command failed: ${getErrorMessage(error)}`);
    }
  });
}
function useRunManualStep() {
  const queryClient2 = useQueryClient();
  const updateStepStatus = useManualControlStore(
    (state) => state.updateStepStatus
  );
  const setCurrentStepIndex = useManualControlStore(
    (state) => state.setCurrentStepIndex
  );
  const sequenceSteps = useManualControlStore((state) => state.sequenceSteps);
  return useMutation({
    mutationFn: async ({
      batchId,
      stepName,
      parameters
    }) => {
      updateStepStatus(stepName, "running");
      const startTime = Date.now();
      const result = await runManualStep(batchId, stepName, parameters);
      const duration = (Date.now() - startTime) / 1e3;
      return { result, duration };
    },
    onSuccess: ({ result, duration }, { batchId, stepName }) => {
      const passed = result.passed !== false;
      updateStepStatus(
        stepName,
        passed ? "completed" : "failed",
        result,
        duration
      );
      if (passed) {
        const currentIndex = sequenceSteps.findIndex(
          (s) => s.name === stepName
        );
        if (currentIndex >= 0 && currentIndex < sequenceSteps.length - 1) {
          setCurrentStepIndex(currentIndex + 1);
        }
      }
      queryClient2.invalidateQueries({
        queryKey: manualQueryKeys.steps(batchId)
      });
      toast.success(`Step "${stepName}" completed`);
    },
    onError: (error, { stepName }) => {
      updateStepStatus(stepName, "failed");
      toast.error(`Step failed: ${getErrorMessage(error)}`);
    }
  });
}
function useSkipManualStep() {
  const queryClient2 = useQueryClient();
  const updateStepStatus = useManualControlStore(
    (state) => state.updateStepStatus
  );
  const setCurrentStepIndex = useManualControlStore(
    (state) => state.setCurrentStepIndex
  );
  const sequenceSteps = useManualControlStore((state) => state.sequenceSteps);
  return useMutation({
    mutationFn: ({
      batchId,
      stepName
    }) => skipManualStep(batchId, stepName),
    onSuccess: (_, { batchId, stepName }) => {
      updateStepStatus(stepName, "skipped");
      const currentIndex = sequenceSteps.findIndex((s) => s.name === stepName);
      if (currentIndex >= 0 && currentIndex < sequenceSteps.length - 1) {
        setCurrentStepIndex(currentIndex + 1);
      }
      queryClient2.invalidateQueries({
        queryKey: manualQueryKeys.steps(batchId)
      });
      toast.info(`Step "${stepName}" skipped`);
    },
    onError: (error) => {
      toast.error(`Failed to skip step: ${getErrorMessage(error)}`);
    }
  });
}
function useResetManualSequence() {
  const queryClient2 = useQueryClient();
  const resetSequence = useManualControlStore((state) => state.resetSequence);
  return useMutation({
    mutationFn: (batchId) => resetManualSequence(batchId),
    onSuccess: (_, batchId) => {
      resetSequence();
      queryClient2.invalidateQueries({
        queryKey: manualQueryKeys.steps(batchId)
      });
      toast.success("Sequence reset");
    },
    onError: (error) => {
      toast.error(`Failed to reset sequence: ${getErrorMessage(error)}`);
    }
  });
}
const pageTitles = {
  "/": "Dashboard",
  "/ui": "Dashboard",
  "/ui/": "Dashboard",
  "/ui/batches": "Batches",
  "/ui/sequences": "Sequences",
  "/ui/manual": "Manual Control",
  "/ui/logs": "Logs",
  "/ui/settings": "Settings"
};
function Header() {
  var _a, _b, _c, _d, _e;
  const location = useLocation();
  const { theme, toggleTheme } = useUIStore();
  const { isOpen, togglePanel, getUnreadCount } = useNotificationStore();
  const isDark = theme === "dark";
  const unreadCount = getUnreadCount();
  const { data: operatorSession } = useOperatorSession();
  const logoutMutation = useOperatorLogout();
  const [userMenuOpen, setUserMenuOpen] = reactExports.useState(false);
  const userMenuRef = reactExports.useRef(null);
  reactExports.useEffect(() => {
    function handleClickOutside(event) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);
  const handleLogout = () => {
    logoutMutation.mutate();
    setUserMenuOpen(false);
  };
  const pageTitle = pageTitles[location.pathname] || "Station UI";
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "header",
    {
      className: "flex items-center justify-between h-[60px] px-5 border-b transition-colors",
      style: {
        backgroundColor: "var(--color-bg-secondary)",
        borderColor: "var(--color-border-default)"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "h1",
          {
            className: "text-lg font-semibold",
            style: { color: "var(--color-text-primary)" },
            children: pageTitle
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
          (operatorSession == null ? void 0 : operatorSession.loggedIn) && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative", ref: userMenuRef, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "button",
              {
                onClick: () => setUserMenuOpen(!userMenuOpen),
                className: "flex items-center gap-2 px-3 py-2 rounded-lg transition-colors",
                style: {
                  color: userMenuOpen ? "var(--color-text-primary)" : "var(--color-text-secondary)",
                  backgroundColor: userMenuOpen ? "var(--color-bg-tertiary)" : "transparent"
                },
                onMouseEnter: (e) => {
                  e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
                  e.currentTarget.style.color = "var(--color-text-primary)";
                },
                onMouseLeave: (e) => {
                  if (!userMenuOpen) {
                    e.currentTarget.style.backgroundColor = "transparent";
                    e.currentTarget.style.color = "var(--color-text-secondary)";
                  }
                },
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(User, { className: "w-5 h-5" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", children: ((_a = operatorSession.operator) == null ? void 0 : _a.name) || ((_b = operatorSession.operator) == null ? void 0 : _b.username) })
                ]
              }
            ),
            userMenuOpen && /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "div",
              {
                className: "absolute right-0 mt-2 w-48 rounded-lg shadow-lg border z-50 py-1",
                style: {
                  backgroundColor: "var(--color-bg-secondary)",
                  borderColor: "var(--color-border-default)"
                },
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsxs(
                    "div",
                    {
                      className: "px-4 py-2 border-b",
                      style: { borderColor: "var(--color-border-default)" },
                      children: [
                        /* @__PURE__ */ jsxRuntimeExports.jsx(
                          "p",
                          {
                            className: "text-sm font-medium",
                            style: { color: "var(--color-text-primary)" },
                            children: ((_c = operatorSession.operator) == null ? void 0 : _c.name) || ((_d = operatorSession.operator) == null ? void 0 : _d.username)
                          }
                        ),
                        /* @__PURE__ */ jsxRuntimeExports.jsx(
                          "p",
                          {
                            className: "text-xs",
                            style: { color: "var(--color-text-tertiary)" },
                            children: (_e = operatorSession.operator) == null ? void 0 : _e.role
                          }
                        )
                      ]
                    }
                  ),
                  /* @__PURE__ */ jsxRuntimeExports.jsxs(
                    "button",
                    {
                      onClick: handleLogout,
                      disabled: logoutMutation.isPending,
                      className: "w-full px-4 py-2 text-left text-sm flex items-center gap-2 transition-colors",
                      style: { color: "var(--color-text-secondary)" },
                      onMouseEnter: (e) => {
                        e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
                        e.currentTarget.style.color = "var(--color-status-error)";
                      },
                      onMouseLeave: (e) => {
                        e.currentTarget.style.backgroundColor = "transparent";
                        e.currentTarget.style.color = "var(--color-text-secondary)";
                      },
                      children: [
                        /* @__PURE__ */ jsxRuntimeExports.jsx(LogOut, { className: "w-4 h-4" }),
                        logoutMutation.isPending ? "Logging out..." : "Logout"
                      ]
                    }
                  )
                ]
              }
            )
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "button",
            {
              onClick: toggleTheme,
              className: "p-2 rounded-lg transition-colors",
              style: {
                color: "var(--color-text-secondary)"
              },
              onMouseEnter: (e) => {
                e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
                e.currentTarget.style.color = "var(--color-text-primary)";
              },
              onMouseLeave: (e) => {
                e.currentTarget.style.backgroundColor = "transparent";
                e.currentTarget.style.color = "var(--color-text-secondary)";
              },
              title: isDark ? "Switch to light mode" : "Switch to dark mode",
              children: isDark ? /* @__PURE__ */ jsxRuntimeExports.jsx(Sun, { className: "w-5 h-5" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Moon, { className: "w-5 h-5" })
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "button",
              {
                "data-notification-trigger": true,
                onClick: togglePanel,
                className: "p-2 rounded-lg transition-colors relative",
                style: {
                  color: isOpen ? "var(--color-text-primary)" : "var(--color-text-secondary)",
                  backgroundColor: isOpen ? "var(--color-bg-tertiary)" : "transparent"
                },
                onMouseEnter: (e) => {
                  e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
                  e.currentTarget.style.color = "var(--color-text-primary)";
                },
                onMouseLeave: (e) => {
                  if (!isOpen) {
                    e.currentTarget.style.backgroundColor = "transparent";
                    e.currentTarget.style.color = "var(--color-text-secondary)";
                  }
                },
                title: "Notifications",
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Bell, { className: "w-5 h-5" }),
                  unreadCount > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx(
                    "span",
                    {
                      className: "absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center text-[10px] font-bold rounded-full px-1",
                      style: {
                        backgroundColor: "var(--color-status-error)",
                        color: "white"
                      },
                      children: unreadCount > 99 ? "99+" : unreadCount
                    }
                  )
                ]
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(NotificationPanel, {})
          ] })
        ] })
      ]
    }
  );
}
function StatusBar() {
  const [currentTime, setCurrentTime] = reactExports.useState(/* @__PURE__ */ new Date());
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  const backendStatus = useConnectionStore((state) => state.backendStatus);
  const batches2 = useBatchStore((state) => state.batches);
  const runningBatches = Array.from(batches2.values()).filter(
    (b) => b.status === "running" || b.status === "starting"
  ).length;
  reactExports.useEffect(() => {
    const timer = setInterval(() => setCurrentTime(/* @__PURE__ */ new Date()), 1e3);
    return () => clearInterval(timer);
  }, []);
  const formatTime = (date) => {
    return date.toLocaleTimeString("ko-KR", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false
    });
  };
  const getStatusColor = (status) => {
    switch (status) {
      case "connected":
        return "fill-green-500 text-green-500";
      case "connecting":
        return "fill-yellow-500 text-yellow-500 animate-pulse";
      case "error":
        return "fill-red-500 text-red-500";
      default:
        return "fill-zinc-500 text-zinc-500";
    }
  };
  const isConnected = websocketStatus === "connected";
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "footer",
    {
      className: "flex items-center justify-between px-4 py-2 text-sm transition-colors",
      style: {
        backgroundColor: "var(--color-bg-secondary)",
        borderTop: "1px solid var(--color-border-default)"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
            isConnected ? /* @__PURE__ */ jsxRuntimeExports.jsx(Wifi, { className: "w-4 h-4", style: { color: "var(--color-success)" } }) : /* @__PURE__ */ jsxRuntimeExports.jsx(WifiOff, { className: "w-4 h-4", style: { color: "var(--color-text-disabled)" } }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "WS" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(Circle, { className: `w-2.5 h-2.5 ${getStatusColor(websocketStatus)}` })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Backend" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(Circle, { className: `w-2.5 h-2.5 ${getStatusColor(backendStatus)}` })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { style: { color: "var(--color-text-secondary)" }, children: [
            "Batches:",
            " ",
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "span",
              {
                className: runningBatches > 0 ? "font-medium" : "",
                style: {
                  color: runningBatches > 0 ? "var(--color-brand-400)" : "var(--color-text-primary)"
                },
                children: [
                  runningBatches,
                  " running"
                ]
              }
            )
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "font-mono", style: { color: "var(--color-text-secondary)" }, children: formatTime(currentTime) })
      ]
    }
  );
}
const Button = reactExports.forwardRef(
  ({
    className = "",
    variant = "primary",
    size = "md",
    isLoading = false,
    disabled,
    children,
    ...props
  }, ref) => {
    const baseClasses = "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
    const variantClasses = {
      primary: "bg-brand-500 text-white hover:bg-brand-600 focus:ring-brand-500",
      secondary: "bg-zinc-200 dark:bg-zinc-700 text-zinc-800 dark:text-white hover:bg-zinc-300 dark:hover:bg-zinc-600 focus:ring-zinc-500",
      danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
      ghost: "bg-transparent text-zinc-700 dark:text-zinc-300 hover:bg-zinc-200 dark:hover:bg-zinc-800 focus:ring-zinc-500"
    };
    const sizeClasses2 = {
      sm: "px-3 py-1.5 text-sm",
      md: "px-4 py-2 text-sm",
      lg: "px-6 py-3 text-base"
    };
    return /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "button",
      {
        ref,
        className: `${baseClasses} ${variantClasses[variant]} ${sizeClasses2[size]} ${className}`,
        disabled: disabled || isLoading,
        ...props,
        children: [
          isLoading && /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-4 h-4 mr-2 animate-spin" }),
          children
        ]
      }
    );
  }
);
Button.displayName = "Button";
const Input = reactExports.forwardRef(
  ({ className = "", label, error, helperText, id, ...props }, ref) => {
    const inputId = id ?? (label == null ? void 0 : label.toLowerCase().replace(/\s+/g, "-"));
    return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "w-full", children: [
      label && /* @__PURE__ */ jsxRuntimeExports.jsx("label", { htmlFor: inputId, className: "block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5", children: label }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "input",
        {
          ref,
          id: inputId,
          className: `w-full px-3 py-2 bg-white dark:bg-zinc-800 border rounded-lg text-zinc-900 dark:text-white placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-colors ${error ? "border-red-500" : "border-zinc-300 dark:border-zinc-700 hover:border-zinc-400 dark:hover:border-zinc-600"} ${className}`,
          ...props
        }
      ),
      error && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-1.5 text-sm text-red-500 dark:text-red-400", children: error }),
      helperText && !error && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-1.5 text-sm text-zinc-600 dark:text-zinc-500", children: helperText })
    ] });
  }
);
Input.displayName = "Input";
const Select = reactExports.forwardRef(
  ({ className = "", label, error, options, placeholder, id, ...props }, ref) => {
    const selectId = id ?? (label == null ? void 0 : label.toLowerCase().replace(/\s+/g, "-"));
    return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "w-full", children: [
      label && /* @__PURE__ */ jsxRuntimeExports.jsx("label", { htmlFor: selectId, className: "block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5", children: label }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "select",
          {
            ref,
            id: selectId,
            className: `w-full px-3 py-2 bg-white dark:bg-zinc-800 border rounded-lg text-zinc-900 dark:text-white appearance-none focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-colors cursor-pointer ${error ? "border-red-500" : "border-zinc-300 dark:border-zinc-700 hover:border-zinc-400 dark:hover:border-zinc-600"} ${className}`,
            ...props,
            children: [
              placeholder && /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "", disabled: true, children: placeholder }),
              options.map((option) => /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: option.value, disabled: option.disabled, children: option.label }, option.value))
            ]
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronDown, { className: "absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 dark:text-zinc-400 pointer-events-none" })
      ] }),
      error && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-1.5 text-sm text-red-500 dark:text-red-400", children: error })
    ] });
  }
);
Select.displayName = "Select";
const variantColors = {
  default: "var(--color-brand-500)",
  success: "#22c55e",
  warning: "#f59e0b",
  error: "#ef4444"
};
const sizeClasses$2 = {
  sm: "h-1",
  md: "h-2",
  lg: "h-3"
};
function ProgressBar({
  value,
  max = 100,
  variant = "default",
  size = "md",
  showLabel = false,
  className = ""
}) {
  const percentage = Math.min(100, Math.max(0, value / max * 100));
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: `w-full ${className}`, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: `w-full rounded-full overflow-hidden ${sizeClasses$2[size]}`,
        style: { backgroundColor: "var(--color-border-default)" },
        children: /* @__PURE__ */ jsxRuntimeExports.jsx(
          "div",
          {
            className: "h-full transition-all duration-300 ease-out",
            style: {
              width: `${percentage}%`,
              backgroundColor: variantColors[variant]
            }
          }
        )
      }
    ),
    showLabel && /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "mt-1 text-xs text-right",
        style: { color: "var(--color-text-secondary)" },
        children: [
          Math.round(percentage),
          "%"
        ]
      }
    )
  ] });
}
const statusConfig = {
  idle: {
    label: "IDLE",
    bg: "rgba(113, 113, 122, 0.2)",
    text: "#a1a1aa",
    dot: "#a1a1aa"
  },
  starting: {
    label: "STARTING",
    bg: "rgba(59, 130, 246, 0.2)",
    text: "#60a5fa",
    dot: "#60a5fa"
  },
  running: {
    label: "RUNNING",
    bg: "rgba(62, 207, 142, 0.2)",
    text: "#3ecf8e",
    dot: "#3ecf8e",
    animate: true
  },
  stopping: {
    label: "STOPPING",
    bg: "rgba(245, 158, 11, 0.2)",
    text: "#fbbf24",
    dot: "#fbbf24"
  },
  completed: {
    label: "COMPLETED",
    bg: "rgba(34, 197, 94, 0.2)",
    text: "#4ade80",
    dot: "#4ade80"
  },
  error: {
    label: "ERROR",
    bg: "rgba(239, 68, 68, 0.2)",
    text: "#f87171",
    dot: "#f87171"
  },
  connected: {
    label: "CONNECTED",
    bg: "rgba(34, 197, 94, 0.2)",
    text: "#4ade80",
    dot: "#4ade80"
  },
  disconnected: {
    label: "DISCONNECTED",
    bg: "rgba(239, 68, 68, 0.2)",
    text: "#f87171",
    dot: "#f87171"
  },
  warning: {
    label: "WARNING",
    bg: "rgba(245, 158, 11, 0.2)",
    text: "#fbbf24",
    dot: "#fbbf24",
    animate: true
  },
  pass: {
    label: "PASS",
    bg: "rgba(34, 197, 94, 0.2)",
    text: "#4ade80",
    dot: "#4ade80"
  },
  fail: {
    label: "FAIL",
    bg: "rgba(239, 68, 68, 0.2)",
    text: "#f87171",
    dot: "#f87171"
  }
};
const sizeClasses$1 = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-2.5 py-1 text-xs"
};
const dotSizeClasses = {
  sm: "w-1.5 h-1.5",
  md: "w-2 h-2"
};
function StatusBadge({ status, size = "md", className = "" }) {
  const config = statusConfig[status] ?? statusConfig["idle"];
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "span",
    {
      className: `inline-flex items-center gap-1.5 rounded-full font-medium ${sizeClasses$1[size]} ${className}`,
      style: { backgroundColor: config.bg, color: config.text },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "span",
          {
            className: `rounded-full ${dotSizeClasses[size]} ${config.animate ? "animate-pulse" : ""}`,
            style: { backgroundColor: config.dot }
          }
        ),
        config.label
      ]
    }
  );
}
function LoadingSpinner({ size = "md", className = "" }) {
  const sizeClasses2 = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8"
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: `flex items-center justify-center ${className}`, children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: `animate-spin text-brand-500 ${sizeClasses2[size]}` }) });
}
function LoadingOverlay({ message = "Loading..." }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col items-center justify-center py-12", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "lg" }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-4 text-sm text-zinc-400", children: message })
  ] });
}
const sizeClasses = {
  sm: "max-w-sm",
  md: "max-w-md",
  lg: "max-w-lg"
};
function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = "md",
  showCloseButton = true
}) {
  const modalRef = reactExports.useRef(null);
  reactExports.useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }
    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);
  function handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
      onClose();
    }
  }
  if (!isOpen) return null;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "fixed inset-0 z-50 flex items-center justify-center p-4",
      onClick: handleBackdropClick,
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "div",
          {
            className: "absolute inset-0 bg-black/60 backdrop-blur-sm",
            "aria-hidden": "true"
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            ref: modalRef,
            className: `relative w-full ${sizeClasses[size]} rounded-xl border shadow-2xl`,
            style: {
              backgroundColor: "var(--color-bg-secondary)",
              borderColor: "var(--color-border-default)"
            },
            role: "dialog",
            "aria-modal": "true",
            "aria-labelledby": "modal-title",
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "div",
                {
                  className: "flex items-center justify-between px-6 py-4 border-b",
                  style: { borderColor: "var(--color-border-default)" },
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(
                      "h2",
                      {
                        id: "modal-title",
                        className: "text-lg font-semibold",
                        style: { color: "var(--color-text-primary)" },
                        children: title
                      }
                    ),
                    showCloseButton && /* @__PURE__ */ jsxRuntimeExports.jsx(
                      "button",
                      {
                        onClick: onClose,
                        className: "p-1 rounded-lg transition-colors",
                        style: { color: "var(--color-text-tertiary)" },
                        onMouseEnter: (e) => {
                          e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
                          e.currentTarget.style.color = "var(--color-text-primary)";
                        },
                        onMouseLeave: (e) => {
                          e.currentTarget.style.backgroundColor = "transparent";
                          e.currentTarget.style.color = "var(--color-text-tertiary)";
                        },
                        "aria-label": "Close modal",
                        children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-5 h-5" })
                      }
                    )
                  ]
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "px-6 py-4", children })
            ]
          }
        )
      ]
    }
  );
}
const typeConfig = {
  success: {
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-5 h-5" }),
    bgColor: "var(--color-status-success)",
    borderColor: "var(--color-status-success)"
  },
  error: {
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-5 h-5" }),
    bgColor: "var(--color-status-error)",
    borderColor: "var(--color-status-error)"
  },
  warning: {
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-5 h-5" }),
    bgColor: "var(--color-status-warning)",
    borderColor: "var(--color-status-warning)"
  },
  info: {
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Info, { className: "w-5 h-5" }),
    bgColor: "var(--color-accent-blue)",
    borderColor: "var(--color-accent-blue)"
  }
};
const DEFAULT_DURATION = 5e3;
function ToastContainer() {
  const [toasts, setToasts] = reactExports.useState([]);
  const removeToast = reactExports.useCallback((id) => {
    setToasts((prev) => prev.filter((toast2) => toast2.id !== id));
  }, []);
  const addToast = reactExports.useCallback((type, message, duration = DEFAULT_DURATION) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const toast2 = { id, type, message, duration };
    setToasts((prev) => [...prev, toast2]);
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration);
    }
  }, [removeToast]);
  reactExports.useEffect(() => {
    const handleToast = (event) => {
      const { type, message, duration } = event.detail;
      addToast(type, message, duration ?? DEFAULT_DURATION);
    };
    window.addEventListener("toast", handleToast);
    return () => window.removeEventListener("toast", handleToast);
  }, [addToast]);
  if (toasts.length === 0) return null;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "fixed top-4 left-1/2 -translate-x-1/2 z-[9999] flex flex-col gap-2 max-w-md", children: [
    toasts.map((toast2) => {
      const config = typeConfig[toast2.type];
      return /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "flex items-start gap-3 p-4 rounded-lg shadow-lg animate-slide-in-down",
          style: {
            backgroundColor: "var(--color-bg-secondary)",
            border: `1px solid ${config.borderColor}`
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { style: { color: config.bgColor }, className: "flex-shrink-0 mt-0.5", children: config.icon }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "p",
              {
                className: "flex-1 text-sm",
                style: { color: "var(--color-text-primary)" },
                children: toast2.message
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "button",
              {
                onClick: () => removeToast(toast2.id),
                className: "flex-shrink-0 p-1 rounded hover:bg-white/10 transition-colors",
                style: { color: "var(--color-text-tertiary)" },
                children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-4 h-4" })
              }
            )
          ]
        },
        toast2.id
      );
    }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("style", { children: `
        @keyframes slide-in-down {
          from {
            transform: translateY(-100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
        .animate-slide-in-down {
          animation: slide-in-down 0.3s ease-out;
        }
      ` })
  ] });
}
function Layout({ children }) {
  const { data: systemInfo, isLoading } = useSystemInfo();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = reactExports.useState(() => {
    const stored = localStorage.getItem("station-sidebar-collapsed");
    return stored ? JSON.parse(stored) : false;
  });
  const stationId = (systemInfo == null ? void 0 : systemInfo.stationId) ?? "...";
  const stationName = (systemInfo == null ? void 0 : systemInfo.stationName) ?? (isLoading ? "Loading..." : "Station");
  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "flex h-screen overflow-hidden transition-colors",
      style: { backgroundColor: "var(--color-bg-primary)" },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Sidebar,
          {
            isCollapsed: isSidebarCollapsed,
            onToggle: toggleSidebar,
            stationId,
            stationName
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 flex flex-col overflow-hidden", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Header, {}),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "main",
            {
              className: "flex-1 p-4 overflow-auto",
              style: { backgroundColor: "var(--color-bg-primary)" },
              children
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBar, {})
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(ToastContainer, {})
      ]
    }
  );
}
const log$1 = createLogger({ prefix: "ErrorBoundary" });
class ErrorBoundary extends reactExports.Component {
  constructor(props) {
    super(props);
    __publicField(this, "handleRetry", () => {
      this.setState({ hasError: false, error: null, errorInfo: null });
    });
    __publicField(this, "handleGoHome", () => {
      window.location.href = "/";
    });
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    var _a, _b;
    this.setState({ errorInfo });
    log$1.error("Caught an error:", error, errorInfo);
    (_b = (_a = this.props).onError) == null ? void 0 : _b.call(_a, error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "min-h-screen flex items-center justify-center bg-zinc-900 p-4", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "max-w-md w-full bg-zinc-800 rounded-lg border border-zinc-700 p-6 text-center", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex justify-center mb-4", children: /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "p-3 bg-red-500/10 rounded-full", children: /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-8 h-8 text-red-500" }) }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-xl font-semibold text-white mb-2", children: "Something went wrong" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-zinc-400 text-sm mb-4", children: "An unexpected error occurred. Please try again or return to the dashboard." }),
        this.state.error && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-4 p-3 bg-zinc-900 rounded-lg text-left", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-zinc-500 mb-1", children: "Error Details:" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-red-400 font-mono break-all", children: this.state.error.message })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-3 justify-center", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "secondary", size: "sm", onClick: this.handleRetry, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "w-4 h-4 mr-2" }),
            "Try Again"
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "primary", size: "sm", onClick: this.handleGoHome, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(House, { className: "w-4 h-4 mr-2" }),
            "Go Home"
          ] })
        ] })
      ] }) });
    }
    return this.props.children;
  }
}
const isIterable = (obj) => Symbol.iterator in obj;
const hasIterableEntries = (value) => (
  // HACK: avoid checking entries type
  "entries" in value
);
const compareEntries = (valueA, valueB) => {
  const mapA = valueA instanceof Map ? valueA : new Map(valueA.entries());
  const mapB = valueB instanceof Map ? valueB : new Map(valueB.entries());
  if (mapA.size !== mapB.size) {
    return false;
  }
  for (const [key, value] of mapA) {
    if (!mapB.has(key) || !Object.is(value, mapB.get(key))) {
      return false;
    }
  }
  return true;
};
const compareIterables = (valueA, valueB) => {
  const iteratorA = valueA[Symbol.iterator]();
  const iteratorB = valueB[Symbol.iterator]();
  let nextA = iteratorA.next();
  let nextB = iteratorB.next();
  while (!nextA.done && !nextB.done) {
    if (!Object.is(nextA.value, nextB.value)) {
      return false;
    }
    nextA = iteratorA.next();
    nextB = iteratorB.next();
  }
  return !!nextA.done && !!nextB.done;
};
function shallow(valueA, valueB) {
  if (Object.is(valueA, valueB)) {
    return true;
  }
  if (typeof valueA !== "object" || valueA === null || typeof valueB !== "object" || valueB === null) {
    return false;
  }
  if (Object.getPrototypeOf(valueA) !== Object.getPrototypeOf(valueB)) {
    return false;
  }
  if (isIterable(valueA) && isIterable(valueB)) {
    if (hasIterableEntries(valueA) && hasIterableEntries(valueB)) {
      return compareEntries(valueA, valueB);
    }
    return compareIterables(valueA, valueB);
  }
  return compareEntries(
    { entries: () => Object.entries(valueA) },
    { entries: () => Object.entries(valueB) }
  );
}
function useShallow(selector) {
  const prev = React.useRef(void 0);
  return (state) => {
    const next = selector(state);
    return shallow(prev.current, next) ? prev.current : prev.current = next;
  };
}
const variantStyles = {
  default: {
    bg: "var(--color-bg-secondary)",
    border: "var(--color-border-default)",
    icon: "var(--color-text-secondary)"
  },
  info: {
    bg: "rgba(59, 130, 246, 0.1)",
    border: "rgba(59, 130, 246, 0.3)",
    icon: "#60a5fa"
  },
  success: {
    bg: "rgba(34, 197, 94, 0.1)",
    border: "rgba(34, 197, 94, 0.3)",
    icon: "#4ade80"
  },
  warning: {
    bg: "rgba(245, 158, 11, 0.1)",
    border: "rgba(245, 158, 11, 0.3)",
    icon: "#fbbf24"
  },
  error: {
    bg: "rgba(239, 68, 68, 0.1)",
    border: "rgba(239, 68, 68, 0.3)",
    icon: "#f87171"
  }
};
function StatsCard({
  title,
  value,
  icon,
  variant = "default",
  trend,
  className = ""
}) {
  const styles = variantStyles[variant];
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: `p-4 rounded-lg border transition-colors ${className}`,
      style: {
        backgroundColor: styles.bg,
        borderColor: styles.border
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: title }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: styles.icon }, children: icon })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "div",
          {
            className: "mt-2 text-3xl font-bold",
            style: { color: "var(--color-text-primary)" },
            children: value
          }
        ),
        trend && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-2 flex items-center gap-1 text-sm", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { style: { color: trend.value >= 0 ? "#4ade80" : "#f87171" }, children: [
            trend.value >= 0 ? "+" : "",
            trend.value,
            "%"
          ] }),
          trend.label && /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: trend.label })
        ] })
      ]
    }
  );
}
const levelStyles = {
  debug: {
    text: "var(--color-text-tertiary)",
    badge: "rgba(113, 113, 122, 0.2)",
    badgeText: "var(--color-text-secondary)"
  },
  info: {
    text: "var(--color-text-primary)",
    badge: "rgba(59, 130, 246, 0.2)",
    badgeText: "#60a5fa"
  },
  warning: {
    text: "#fbbf24",
    badge: "rgba(245, 158, 11, 0.2)",
    badgeText: "#fbbf24"
  },
  error: {
    text: "#f87171",
    badge: "rgba(239, 68, 68, 0.2)",
    badgeText: "#f87171"
  }
};
function LogEntryRow$1({ log: log2, showBatchId = true }) {
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    });
  };
  const styles = levelStyles[log2.level];
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "flex items-start gap-3 py-1.5 px-2 rounded text-sm font-mono transition-colors",
      style: { backgroundColor: "transparent" },
      onMouseEnter: (e) => {
        e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
      },
      onMouseLeave: (e) => {
        e.currentTarget.style.backgroundColor = "transparent";
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "span",
          {
            className: "text-xs w-20 flex-shrink-0",
            style: { color: "var(--color-text-tertiary)" },
            children: formatTime(log2.timestamp)
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "span",
          {
            className: "px-1.5 py-0.5 rounded text-xs uppercase w-16 text-center flex-shrink-0",
            style: { backgroundColor: styles.badge, color: styles.badgeText },
            children: log2.level
          }
        ),
        showBatchId && log2.batchId && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex-shrink-0", style: { color: "var(--color-text-tertiary)" }, children: [
          "[",
          log2.batchId,
          "]"
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "flex-1 break-all", style: { color: styles.text }, children: log2.message })
      ]
    }
  );
}
function BatchOverviewCard({ batch }) {
  const navigate = useNavigate();
  const handleClick = () => {
    navigate(`/batches/${batch.id}`);
  };
  const statusConfig2 = getStatusConfig(batch.status);
  const progressPercent = Math.round(batch.progress * 100);
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      onClick: handleClick,
      className: "p-4 rounded-lg border transition-all cursor-pointer hover:shadow-md hover:border-brand-400",
      style: {
        backgroundColor: "var(--color-bg-secondary)",
        borderColor: "var(--color-border-default)"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-start justify-between gap-2 mb-3", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "h4",
            {
              className: "text-sm font-semibold truncate flex-1",
              style: { color: "var(--color-text-primary)" },
              title: batch.name,
              children: batch.name
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "div",
            {
              className: "flex-shrink-0 p-1.5 rounded-full",
              style: { backgroundColor: statusConfig2.bgColor },
              children: /* @__PURE__ */ jsxRuntimeExports.jsx(statusConfig2.icon, { className: "w-4 h-4", style: { color: statusConfig2.iconColor } })
            }
          )
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "mb-3", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
          "span",
          {
            className: "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium uppercase tracking-wide",
            style: {
              backgroundColor: statusConfig2.badgeBg,
              color: statusConfig2.badgeText
            },
            children: batch.status
          }
        ) }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-3", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-1.5", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Progress" }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "span",
              {
                className: "text-sm font-semibold",
                style: { color: "var(--color-text-primary)" },
                children: [
                  progressPercent,
                  "%"
                ]
              }
            )
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            ProgressBar,
            {
              value: progressPercent,
              variant: getProgressVariant(batch.status, batch.lastRunPassed),
              size: "md"
            }
          )
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "pt-3 border-t",
            style: { borderColor: "var(--color-border-muted)" },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Step" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "p",
                {
                  className: "text-sm font-medium truncate mt-0.5",
                  style: { color: "var(--color-text-secondary)" },
                  title: batch.currentStep || "No step",
                  children: batch.currentStep || "-"
                }
              )
            ]
          }
        )
      ]
    }
  );
}
function getStatusConfig(status) {
  switch (status) {
    case "completed":
      return {
        icon: CircleCheckBig,
        iconColor: "var(--color-success)",
        bgColor: "var(--color-success-bg)",
        badgeBg: "var(--color-success-bg)",
        badgeText: "var(--color-success)"
      };
    case "error":
      return {
        icon: CircleX,
        iconColor: "var(--color-error)",
        bgColor: "var(--color-error-bg)",
        badgeBg: "var(--color-error-bg)",
        badgeText: "var(--color-error)"
      };
    case "running":
      return {
        icon: LoaderCircle,
        iconColor: "var(--color-info)",
        bgColor: "var(--color-info-bg)",
        badgeBg: "var(--color-info-bg)",
        badgeText: "var(--color-info)"
      };
    case "starting":
      return {
        icon: Clock,
        iconColor: "var(--color-warning)",
        bgColor: "var(--color-warning-bg)",
        badgeBg: "var(--color-warning-bg)",
        badgeText: "var(--color-warning)"
      };
    case "stopping":
      return {
        icon: CircleStop,
        iconColor: "var(--color-warning)",
        bgColor: "var(--color-warning-bg)",
        badgeBg: "var(--color-warning-bg)",
        badgeText: "var(--color-warning)"
      };
    case "idle":
    default:
      return {
        icon: CircleAlert,
        iconColor: "var(--color-text-tertiary)",
        bgColor: "var(--color-bg-tertiary)",
        badgeBg: "var(--color-bg-tertiary)",
        badgeText: "var(--color-text-secondary)"
      };
  }
}
function getProgressVariant(status, lastRunPassed) {
  if (status === "error") return "error";
  if (status === "completed") {
    return lastRunPassed === false ? "error" : "success";
  }
  if (status === "stopping") return "warning";
  return "default";
}
function DashboardPage() {
  const { data: batches2, isLoading: batchesLoading, isError: batchesError, refetch: refetchBatches } = useBatchList();
  const { data: health, isError: healthError, isLoading: healthLoading, refetch: refetchHealth } = useHealthStatus();
  const { data: systemInfo } = useSystemInfo();
  const { data: allStatistics } = useAllBatchStatistics();
  const { subscribe, unsubscribe } = useWebSocket();
  const setAllBatchStatistics = useBatchStore((state) => state.setAllBatchStatistics);
  const batchStatistics = useBatchStore(useShallow((state) => state.batchStatistics));
  const totalStats = reactExports.useMemo(() => {
    const total = { total: 0, passCount: 0, fail: 0, passRate: 0 };
    batchStatistics.forEach((s) => {
      total.total += s.total;
      total.passCount += s.passCount;
      total.fail += s.fail;
    });
    total.passRate = total.total > 0 ? total.passCount / total.total : 0;
    return total;
  }, [batchStatistics]);
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  const setBackendStatus = useConnectionStore((state) => state.setBackendStatus);
  reactExports.useEffect(() => {
    if (health) {
      setBackendStatus(health.backendStatus === "connected" ? "connected" : "disconnected");
    } else if (healthError) {
      setBackendStatus("disconnected");
    }
  }, [health, healthError, setBackendStatus]);
  reactExports.useEffect(() => {
    if (allStatistics) {
      setAllBatchStatistics(allStatistics);
    }
  }, [allStatistics, setAllBatchStatistics]);
  const batchesMap = useBatchStore(useShallow((state) => state.batches));
  const storeBatches = reactExports.useMemo(() => Array.from(batchesMap.values()), [batchesMap]);
  const logs = useLogStore(useShallow((state) => state.logs.slice(-10)));
  reactExports.useEffect(() => {
    if (batches2 && batches2.length > 0) {
      const batchIds = batches2.map((b) => b.id);
      subscribe(batchIds);
      return () => unsubscribe(batchIds);
    }
  }, [batches2, subscribe, unsubscribe]);
  const displayBatches = storeBatches.length > 0 ? storeBatches : batches2 ?? [];
  const isStationServiceConnected = !healthError && !batchesError;
  const handleRetry = () => {
    refetchBatches();
    refetchHealth();
  };
  if (batchesLoading && !batches2) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingOverlay, { message: "Loading dashboard..." });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    !isStationServiceConnected && /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "p-4 rounded-lg border flex items-center justify-between",
        style: {
          backgroundColor: "var(--color-error-bg)",
          borderColor: "var(--color-error)"
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(ServerOff, { className: "w-5 h-5", style: { color: "var(--color-error)" } }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-medium", style: { color: "var(--color-error)" }, children: "Station Service Disconnected" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: "Unable to connect to station service. Check if the service is running." })
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "button",
            {
              onClick: handleRetry,
              className: "flex items-center gap-2 px-3 py-1.5 rounded text-sm font-medium transition-colors",
              style: {
                backgroundColor: "var(--color-bg-secondary)",
                color: "var(--color-text-primary)",
                border: "1px solid var(--color-border-default)"
              },
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "w-4 h-4" }),
                "Retry"
              ]
            }
          )
        ]
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        StatsCard,
        {
          title: "Total Runs",
          value: totalStats.total,
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Activity, { className: "w-5 h-5" }),
          variant: "default"
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        StatsCard,
        {
          title: "Pass",
          value: totalStats.passCount,
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-5 h-5" }),
          variant: "success"
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        StatsCard,
        {
          title: "Fail",
          value: totalStats.fail,
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-5 h-5" }),
          variant: "error"
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "p-4 rounded-lg border transition-colors",
        style: {
          backgroundColor: "var(--color-bg-secondary)",
          borderColor: "var(--color-border-default)"
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "h3",
            {
              className: "text-lg font-semibold mb-3",
              style: { color: "var(--color-text-primary)" },
              children: "System Health"
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-3 gap-4 text-sm", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Station Service" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "mt-1", children: healthLoading ? /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Checking..." }) : /* @__PURE__ */ jsxRuntimeExports.jsx(
                StatusBadge,
                {
                  status: isStationServiceConnected ? (health == null ? void 0 : health.status) === "healthy" ? "connected" : "warning" : "disconnected",
                  size: "sm"
                }
              ) })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Backend (MES)" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "mt-1", children: !isStationServiceConnected ? /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge, { status: "disconnected", size: "sm" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(
                StatusBadge,
                {
                  status: (health == null ? void 0 : health.backendStatus) === "connected" ? "connected" : "disconnected",
                  size: "sm"
                }
              ) })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "WebSocket" }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-1 flex items-center gap-2", children: [
                websocketStatus === "disconnected" && /* @__PURE__ */ jsxRuntimeExports.jsx(WifiOff, { className: "w-3.5 h-3.5", style: { color: "var(--color-text-disabled)" } }),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  StatusBadge,
                  {
                    status: websocketStatus === "connected" ? "connected" : websocketStatus === "connecting" ? "warning" : "disconnected",
                    size: "sm"
                  }
                )
              ] })
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-4 pt-4", style: { borderTop: "1px solid var(--color-border-muted)" }, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-2", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: "Disk Usage" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: isStationServiceConnected && (health == null ? void 0 : health.diskUsage) != null && !isNaN(health.diskUsage) ? `${health.diskUsage.toFixed(1)}%` : "-" })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              ProgressBar,
              {
                value: isStationServiceConnected && (health == null ? void 0 : health.diskUsage) != null && !isNaN(health.diskUsage) ? health.diskUsage : 0,
                variant: !isStationServiceConnected ? "default" : (health == null ? void 0 : health.diskUsage) != null && health.diskUsage > 90 ? "error" : (health == null ? void 0 : health.diskUsage) != null && health.diskUsage > 80 ? "warning" : "default",
                size: "sm"
              }
            )
          ] }),
          systemInfo && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-4 pt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs", style: { borderTop: "1px solid var(--color-border-muted)" }, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Station ID" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { style: { color: "var(--color-text-secondary)" }, children: systemInfo.stationId })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Station Name" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { style: { color: "var(--color-text-secondary)" }, children: systemInfo.stationName })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Version" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { style: { color: "var(--color-text-secondary)" }, children: systemInfo.version })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Uptime" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { style: { color: "var(--color-text-secondary)" }, children: formatUptime$1(systemInfo.uptime) })
            ] })
          ] })
        ]
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "h3",
        {
          className: "text-lg font-semibold mb-4",
          style: { color: "var(--color-text-primary)" },
          children: "Batch Status Overview"
        }
      ),
      displayBatches.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx(
        "div",
        {
          className: "p-4 rounded-lg border",
          style: {
            backgroundColor: "var(--color-bg-secondary)",
            borderColor: "var(--color-border-default)"
          },
          children: /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: "No batches configured" })
        }
      ) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4", children: displayBatches.map((batch) => /* @__PURE__ */ jsxRuntimeExports.jsx(BatchOverviewCard, { batch }, batch.id)) })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "p-4 rounded-lg border transition-colors",
        style: {
          backgroundColor: "var(--color-bg-secondary)",
          borderColor: "var(--color-border-default)"
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "h3",
            {
              className: "text-lg font-semibold mb-4",
              style: { color: "var(--color-text-primary)" },
              children: "Recent Activity"
            }
          ),
          logs.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: "No recent activity" }) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-1 max-h-64 overflow-y-auto", children: logs.slice().reverse().map((log2) => /* @__PURE__ */ jsxRuntimeExports.jsx(LogEntryRow$1, { log: log2, showBatchId: true }, log2.id)) })
        ]
      }
    )
  ] });
}
function formatUptime$1(seconds) {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor(seconds % 3600 / 60);
  if (hours < 24) return `${hours}h ${minutes}m`;
  const days = Math.floor(hours / 24);
  return `${days}d ${hours % 24}h`;
}
function BatchCard({
  batch,
  statistics,
  onStart,
  onStop,
  onDelete,
  onSelect,
  isLoading,
  isSelected
}) {
  const isRunning = batch.status === "running" || batch.status === "starting";
  const canStart = batch.status === "idle" || batch.status === "completed" || batch.status === "error";
  const stats = statistics || { total: 0, passCount: 0, fail: 0, passRate: 0 };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: `p-4 rounded-lg border transition-all cursor-pointer ${isSelected ? "border-brand-500 ring-1 ring-brand-500/50" : "hover:opacity-90"}`,
      style: {
        backgroundColor: "var(--color-bg-secondary)",
        borderColor: isSelected ? void 0 : "var(--color-border-default)"
      },
      onClick: () => onSelect == null ? void 0 : onSelect(batch.id),
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-3", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: batch.name }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge, { status: batch.status, size: "sm" })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1", onClick: (e) => e.stopPropagation(), children: [
            canStart && onStart && /* @__PURE__ */ jsxRuntimeExports.jsx(
              Button,
              {
                variant: "ghost",
                size: "sm",
                onClick: () => onStart(batch.id),
                disabled: isLoading,
                title: "Start",
                children: /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-4 h-4" })
              }
            ),
            isRunning && onStop && /* @__PURE__ */ jsxRuntimeExports.jsx(
              Button,
              {
                variant: "ghost",
                size: "sm",
                onClick: () => onStop(batch.id),
                disabled: isLoading,
                title: "Stop",
                children: /* @__PURE__ */ jsxRuntimeExports.jsx(Square, { className: "w-4 h-4" })
              }
            ),
            !isRunning && onDelete && /* @__PURE__ */ jsxRuntimeExports.jsx(
              Button,
              {
                variant: "ghost",
                size: "sm",
                onClick: () => onDelete(batch.id),
                disabled: isLoading,
                title: "Delete",
                className: "text-red-500 hover:text-red-400 hover:bg-red-500/10",
                children: /* @__PURE__ */ jsxRuntimeExports.jsx(Trash2, { className: "w-4 h-4" })
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronRight, { className: "w-4 h-4", style: { color: "var(--color-text-tertiary)" } })
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2 mb-3", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            ProgressBar,
            {
              value: batch.progress * 100,
              variant: batch.status === "error" ? "error" : batch.status === "completed" ? batch.lastRunPassed === false ? "error" : "success" : "default",
              size: "sm"
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-xs w-12 text-right", style: { color: "var(--color-text-secondary)" }, children: [
            Math.round(batch.progress * 100),
            "%"
          ] })
        ] }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 text-xs mb-3", style: { color: "var(--color-text-tertiary)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Layers, { className: "w-3 h-3" }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "truncate", children: [
            batch.sequenceName || "No sequence",
            batch.sequenceVersion && ` v${batch.sequenceVersion}`
          ] })
        ] }),
        batch.currentStep && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 text-xs mb-3 p-2 rounded", style: { backgroundColor: "var(--color-bg-tertiary)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-3 h-3 text-brand-500" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Step:" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium truncate", style: { color: "var(--color-text-primary)" }, children: batch.currentStep }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "ml-auto", style: { color: "var(--color-text-tertiary)" }, children: [
            "(",
            (batch.stepIndex ?? 0) + 1,
            "/",
            batch.totalSteps ?? 0,
            ")"
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-4 pt-3 border-t", style: { borderColor: "var(--color-border-default)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            StatBadge,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Layers, { className: "w-3 h-3", style: { color: "var(--color-text-secondary)" } }),
              value: stats.total,
              label: "Total"
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            StatBadge,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-3 h-3 text-green-500" }),
              value: stats.passCount,
              label: "Pass",
              color: "text-green-500"
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            StatBadge,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-3 h-3 text-red-500" }),
              value: stats.fail,
              label: "Fail",
              color: "text-red-500"
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "ml-auto", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
            "span",
            {
              className: `text-sm font-medium ${stats.passRate >= 0.9 ? "text-green-500" : stats.passRate >= 0.7 ? "text-yellow-500" : stats.passRate > 0 ? "text-red-500" : "text-zinc-500"}`,
              children: stats.total > 0 ? `${(stats.passRate * 100).toFixed(0)}%` : "-"
            }
          ) })
        ] })
      ]
    }
  );
}
function StatBadge({
  icon,
  value,
  label,
  color
}) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1.5", title: label, children: [
    icon,
    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: `text-sm font-medium ${color || ""}`, style: color ? void 0 : { color: "var(--color-text-primary)" }, children: value })
  ] });
}
function BatchList({ batches: batches2, statistics, onStart, onStop, onDelete, onSelect, isLoading }) {
  const { batchId: selectedBatchId } = useParams();
  const [statusFilter, setStatusFilter] = reactExports.useState("all");
  const batchStatistics = useBatchStore((state) => state.batchStatistics);
  const batchStats = statistics || batchStatistics;
  const filteredBatches = statusFilter === "all" ? batches2 : batches2.filter((b) => b.status === statusFilter);
  const statusOptions = [
    { value: "all", label: "All Status" },
    { value: "idle", label: "Idle" },
    { value: "running", label: "Running" },
    { value: "completed", label: "Completed" },
    { value: "error", label: "Error" }
  ];
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("h3", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: [
        "Batches (",
        filteredBatches.length,
        ")"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-40", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
        Select,
        {
          options: statusOptions,
          value: statusFilter,
          onChange: (e) => setStatusFilter(e.target.value)
        }
      ) })
    ] }),
    filteredBatches.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "p-8 text-center rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)", color: "var(--color-text-tertiary)" }, children: statusFilter === "all" ? "No batches configured" : `No ${statusFilter} batches` }) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid gap-4", children: filteredBatches.map((batch) => /* @__PURE__ */ jsxRuntimeExports.jsx(
      BatchCard,
      {
        batch,
        statistics: batchStats.get(batch.id),
        onStart,
        onStop,
        onDelete,
        onSelect,
        isLoading,
        isSelected: batch.id === selectedBatchId
      },
      batch.id
    )) })
  ] });
}
const WIZARD_STEPS = [
  { key: "sequence", label: "Select Sequence" },
  { key: "steps", label: "Configure Steps" },
  { key: "parameters", label: "Set Parameters" },
  { key: "quantity", label: "Batch Quantity" },
  { key: "review", label: "Review & Create" }
];
function CreateBatchWizard({
  isOpen,
  onClose,
  onSubmit,
  sequences,
  getSequenceDetail,
  isSubmitting
}) {
  const [currentStep, setCurrentStep] = reactExports.useState("sequence");
  const [selectedSequence, setSelectedSequence] = reactExports.useState("");
  const [sequenceDetail, setSequenceDetail] = reactExports.useState(null);
  const [isLoadingSequence, setIsLoadingSequence] = reactExports.useState(false);
  const [stepOrder, setStepOrder] = reactExports.useState([]);
  const [parameters, setParameters] = reactExports.useState({});
  const [quantity, setQuantity] = reactExports.useState(1);
  const [draggedIndex, setDraggedIndex] = reactExports.useState(null);
  const currentStepIndex = WIZARD_STEPS.findIndex((s) => s.key === currentStep);
  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === WIZARD_STEPS.length - 1;
  reactExports.useEffect(() => {
    if (isOpen) {
      setCurrentStep("sequence");
      setSelectedSequence("");
      setSequenceDetail(null);
      setIsLoadingSequence(false);
      setStepOrder([]);
      setParameters({});
      setQuantity(1);
      setDraggedIndex(null);
    }
  }, [isOpen]);
  const handleSequenceSelect = reactExports.useCallback(
    async (sequenceName) => {
      setSelectedSequence(sequenceName);
      if (!sequenceName) {
        setSequenceDetail(null);
        setStepOrder([]);
        setParameters({});
        return;
      }
      setIsLoadingSequence(true);
      try {
        const detail = await getSequenceDetail(sequenceName);
        setSequenceDetail(detail);
        setStepOrder(
          detail.steps.map((step) => ({
            name: step.name,
            displayName: step.displayName,
            order: step.order,
            enabled: true
          }))
        );
        const defaultParams = {};
        detail.parameters.forEach((param) => {
          defaultParams[param.name] = param.default;
        });
        setParameters(defaultParams);
      } catch (error) {
        console.error("Failed to load sequence:", error);
      } finally {
        setIsLoadingSequence(false);
      }
    },
    [getSequenceDetail]
  );
  const goNext = () => {
    const nextIndex = currentStepIndex + 1;
    const nextStep = WIZARD_STEPS[nextIndex];
    if (nextStep) {
      setCurrentStep(nextStep.key);
    }
  };
  const goBack = () => {
    const prevIndex = currentStepIndex - 1;
    const prevStep = WIZARD_STEPS[prevIndex];
    if (prevStep) {
      setCurrentStep(prevStep.key);
    }
  };
  const handleDragStart = (index) => {
    setDraggedIndex(index);
  };
  const handleDragOver = (e, index) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;
    const newOrder = [...stepOrder];
    const draggedItem = newOrder[draggedIndex];
    if (!draggedItem) return;
    newOrder.splice(draggedIndex, 1);
    newOrder.splice(index, 0, draggedItem);
    newOrder.forEach((item, i) => {
      item.order = i + 1;
    });
    setStepOrder(newOrder);
    setDraggedIndex(index);
  };
  const handleDragEnd = () => {
    setDraggedIndex(null);
  };
  const toggleStepEnabled = (index) => {
    setStepOrder(
      (prev) => prev.map((item, i) => i === index ? { ...item, enabled: !item.enabled } : item)
    );
  };
  const handleParamChange = (name, value) => {
    setParameters((prev) => ({ ...prev, [name]: value }));
  };
  const handleSubmit = () => {
    const request = {
      quantity,
      sequenceName: selectedSequence,
      stepOrder: stepOrder.filter((s) => s.enabled),
      parameters
    };
    onSubmit(request);
  };
  const canProceed = reactExports.useMemo(() => {
    switch (currentStep) {
      case "sequence":
        return !!selectedSequence && !!sequenceDetail;
      case "steps":
        return stepOrder.filter((s) => s.enabled).length > 0;
      case "parameters":
        return true;
      // Parameters are optional
      case "quantity":
        return quantity >= 1 && quantity <= 100;
      case "review":
        return true;
      default:
        return false;
    }
  }, [currentStep, selectedSequence, sequenceDetail, stepOrder, quantity]);
  if (!isOpen) return null;
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "w-full max-w-5xl rounded-xl border flex flex-col overflow-hidden", style: { height: "700px", minHeight: "700px", maxHeight: "700px", backgroundColor: "var(--color-bg-primary)", borderColor: "var(--color-border-default)" }, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between p-4 border-b", style: { borderColor: "var(--color-border-default)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-xl font-bold", style: { color: "var(--color-text-primary)" }, children: "Create Batch" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: onClose, children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-5 h-5" }) })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "px-6 py-4 border-b", style: { borderColor: "var(--color-border-default)", backgroundColor: "var(--color-bg-secondary)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-between", children: WIZARD_STEPS.map((step, index) => /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center flex-shrink-0", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "div",
        {
          className: `flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium flex-shrink-0 ${index < currentStepIndex ? "bg-brand-500 text-white" : index === currentStepIndex ? "bg-brand-500/20 text-brand-500 border-2 border-brand-500" : ""}`,
          style: index >= currentStepIndex && index !== currentStepIndex ? { backgroundColor: "var(--color-bg-tertiary)", color: "var(--color-text-tertiary)" } : void 0,
          children: index < currentStepIndex ? /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "w-4 h-4" }) : index + 1
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "span",
        {
          className: "ml-2 text-sm whitespace-nowrap",
          style: { color: index === currentStepIndex ? "var(--color-text-primary)" : "var(--color-text-tertiary)" },
          children: step.label
        }
      ),
      index < WIZARD_STEPS.length - 1 && /* @__PURE__ */ jsxRuntimeExports.jsx(
        "div",
        {
          className: `w-8 lg:w-12 h-0.5 mx-2 flex-shrink-0 ${index < currentStepIndex ? "bg-brand-500" : ""}`,
          style: index >= currentStepIndex ? { backgroundColor: "var(--color-border-default)" } : void 0
        }
      )
    ] }, step.key)) }) }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 min-h-0 overflow-y-auto p-6", children: [
      currentStep === "sequence" && /* @__PURE__ */ jsxRuntimeExports.jsx(
        SequenceSelectStep,
        {
          sequences,
          selectedSequence,
          onSelect: handleSequenceSelect,
          sequenceDetail,
          isLoading: isLoadingSequence
        }
      ),
      currentStep === "steps" && sequenceDetail && /* @__PURE__ */ jsxRuntimeExports.jsx(
        StepConfigStep,
        {
          steps: sequenceDetail.steps,
          stepOrder,
          onDragStart: handleDragStart,
          onDragOver: handleDragOver,
          onDragEnd: handleDragEnd,
          onToggleEnabled: toggleStepEnabled,
          draggedIndex
        }
      ),
      currentStep === "parameters" && sequenceDetail && /* @__PURE__ */ jsxRuntimeExports.jsx(
        ParameterConfigStep,
        {
          parameterSchemas: sequenceDetail.parameters,
          parameters,
          onChange: handleParamChange
        }
      ),
      currentStep === "quantity" && /* @__PURE__ */ jsxRuntimeExports.jsx(QuantityStep, { quantity, onChange: setQuantity }),
      currentStep === "review" && /* @__PURE__ */ jsxRuntimeExports.jsx(
        ReviewStep,
        {
          sequenceName: selectedSequence,
          sequenceDetail,
          stepOrder,
          parameters,
          quantity
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between p-4 border-t", style: { borderColor: "var(--color-border-default)", backgroundColor: "var(--color-bg-secondary)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "ghost", onClick: goBack, disabled: isFirstStep, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronLeft, { className: "w-4 h-4 mr-1" }),
        "Back"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", onClick: onClose, children: "Cancel" }),
        isLastStep ? /* @__PURE__ */ jsxRuntimeExports.jsxs(
          Button,
          {
            variant: "primary",
            onClick: handleSubmit,
            disabled: !canProceed,
            isLoading: isSubmitting,
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "w-4 h-4 mr-1" }),
              "Create Batches"
            ]
          }
        ) : /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "primary", onClick: goNext, disabled: !canProceed, children: [
          "Next",
          /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronRight, { className: "w-4 h-4 ml-1" })
        ] })
      ] })
    ] })
  ] }) });
}
function SequenceSelectStep({
  sequences,
  selectedSequence,
  onSelect,
  sequenceDetail,
  isLoading
}) {
  const sequenceOptions = [
    { value: "", label: "Select a sequence..." },
    ...sequences.map((s) => ({
      value: s.name,
      label: `${s.displayName || s.name} (v${s.version})`
    }))
  ];
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-medium mb-2", style: { color: "var(--color-text-primary)" }, children: "Select Deployed Sequence" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mb-4", style: { color: "var(--color-text-secondary)" }, children: "Choose a deployed sequence to use for this batch. Each batch can use a different sequence." }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Select,
        {
          options: sequenceOptions,
          value: selectedSequence,
          onChange: (e) => onSelect(e.target.value),
          className: "w-full"
        }
      )
    ] }),
    isLoading && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-center py-8", children: /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "animate-spin w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full" }) }),
    sequenceDetail && !isLoading && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "font-medium mb-3", style: { color: "var(--color-text-primary)" }, children: "Sequence Details" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-2 gap-4 text-sm", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Name:" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "ml-2", style: { color: "var(--color-text-primary)" }, children: sequenceDetail.displayName || sequenceDetail.name })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Version:" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "ml-2", style: { color: "var(--color-text-primary)" }, children: sequenceDetail.version })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Steps:" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "ml-2", style: { color: "var(--color-text-primary)" }, children: sequenceDetail.steps.length })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Parameters:" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "ml-2", style: { color: "var(--color-text-primary)" }, children: sequenceDetail.parameters.length })
        ] }),
        sequenceDetail.description && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "col-span-2", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Description:" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-1", style: { color: "var(--color-text-primary)" }, children: sequenceDetail.description })
        ] })
      ] })
    ] })
  ] });
}
function StepConfigStep({
  steps,
  stepOrder,
  onDragStart,
  onDragOver,
  onDragEnd,
  onToggleEnabled,
  draggedIndex
}) {
  const getStepInfo = (name) => steps.find((s) => s.name === name);
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-medium mb-2", style: { color: "var(--color-text-primary)" }, children: "Configure Steps" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mb-4", style: { color: "var(--color-text-secondary)" }, children: "Drag to reorder steps or toggle to enable/disable them." })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2", children: stepOrder.map((item, index) => {
      const stepInfo = getStepInfo(item.name);
      return /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          draggable: true,
          onDragStart: () => onDragStart(index),
          onDragOver: (e) => onDragOver(e, index),
          onDragEnd,
          className: `flex items-center gap-3 p-3 rounded-lg border transition-all ${draggedIndex === index ? "bg-brand-500/20 border-brand-500" : item.enabled ? "hover:opacity-90" : "opacity-60"}`,
          style: {
            backgroundColor: draggedIndex === index ? void 0 : "var(--color-bg-secondary)",
            borderColor: draggedIndex === index ? void 0 : "var(--color-border-default)"
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "cursor-grab", children: /* @__PURE__ */ jsxRuntimeExports.jsx(GripVertical, { className: "w-5 h-5", style: { color: "var(--color-text-tertiary)" } }) }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-8 h-8 flex items-center justify-center rounded-full text-sm font-medium", style: { backgroundColor: "var(--color-bg-tertiary)", color: "var(--color-text-primary)" }, children: index + 1 }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-medium", style: { color: item.enabled ? "var(--color-text-primary)" : "var(--color-text-tertiary)" }, children: (stepInfo == null ? void 0 : stepInfo.displayName) || item.name }),
              (stepInfo == null ? void 0 : stepInfo.description) && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs mt-0.5", style: { color: "var(--color-text-tertiary)" }, children: stepInfo.description })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 text-xs", style: { color: "var(--color-text-tertiary)" }, children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
                "Timeout: ",
                (stepInfo == null ? void 0 : stepInfo.timeout) || 0,
                "s"
              ] }),
              (stepInfo == null ? void 0 : stepInfo.retry) && stepInfo.retry > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
                "Retry: ",
                stepInfo.retry
              ] })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Button,
              {
                variant: item.enabled ? "ghost" : "secondary",
                size: "sm",
                onClick: () => onToggleEnabled(index),
                children: item.enabled ? "Enabled" : "Disabled"
              }
            )
          ]
        },
        item.name
      );
    }) }),
    stepOrder.filter((s) => s.enabled).length === 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(CircleAlert, { className: "w-4 h-4" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", children: "At least one step must be enabled" })
    ] })
  ] });
}
function ParameterConfigStep({
  parameterSchemas,
  parameters,
  onChange
}) {
  if (parameterSchemas.length === 0) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "text-center py-8", children: /* @__PURE__ */ jsxRuntimeExports.jsx("p", { style: { color: "var(--color-text-tertiary)" }, children: "This sequence has no configurable parameters" }) });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-medium mb-2", style: { color: "var(--color-text-primary)" }, children: "Set Parameters" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mb-4", style: { color: "var(--color-text-secondary)" }, children: "Configure the sequence parameters. Default values are pre-filled." })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: parameterSchemas.map((param) => /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-3 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("label", { className: "block text-sm font-medium mb-1", style: { color: "var(--color-text-primary)" }, children: [
        param.displayName || param.name,
        param.unit && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "ml-1", style: { color: "var(--color-text-tertiary)" }, children: [
          "(",
          param.unit,
          ")"
        ] })
      ] }),
      param.description && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs mb-2", style: { color: "var(--color-text-tertiary)" }, children: param.description }),
      param.type === "boolean" ? /* @__PURE__ */ jsxRuntimeExports.jsx(
        Select,
        {
          options: [
            { value: "true", label: "True" },
            { value: "false", label: "False" }
          ],
          value: String(parameters[param.name]),
          onChange: (e) => onChange(param.name, e.target.value === "true")
        }
      ) : param.options ? /* @__PURE__ */ jsxRuntimeExports.jsx(
        Select,
        {
          options: param.options.map((opt) => ({ value: opt, label: opt })),
          value: String(parameters[param.name]),
          onChange: (e) => onChange(param.name, e.target.value)
        }
      ) : /* @__PURE__ */ jsxRuntimeExports.jsx(
        Input,
        {
          type: param.type === "integer" || param.type === "float" ? "number" : "text",
          value: String(parameters[param.name] ?? ""),
          onChange: (e) => {
            const val = e.target.value;
            if (param.type === "integer") {
              onChange(param.name, parseInt(val, 10) || 0);
            } else if (param.type === "float") {
              onChange(param.name, parseFloat(val) || 0);
            } else {
              onChange(param.name, val);
            }
          },
          min: param.min,
          max: param.max
        }
      ),
      (param.min !== void 0 || param.max !== void 0) && /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs mt-1", style: { color: "var(--color-text-tertiary)" }, children: [
        "Range: ",
        param.min ?? "-∞",
        " ~ ",
        param.max ?? "∞"
      ] })
    ] }, param.name)) })
  ] });
}
function QuantityStep({
  quantity,
  onChange
}) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-medium mb-2", style: { color: "var(--color-text-primary)" }, children: "Batch Quantity" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mb-4", style: { color: "var(--color-text-secondary)" }, children: "Select the number of batches to create. Each batch will be configured with the same sequence and parameters." })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-center gap-6", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Button,
        {
          variant: "secondary",
          size: "lg",
          onClick: () => onChange(Math.max(1, quantity - 1)),
          disabled: quantity <= 1,
          children: /* @__PURE__ */ jsxRuntimeExports.jsx(Minus, { className: "w-5 h-5" })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-24", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
        Input,
        {
          type: "number",
          value: quantity,
          onChange: (e) => {
            const val = parseInt(e.target.value, 10);
            if (!isNaN(val) && val >= 1 && val <= 100) {
              onChange(val);
            }
          },
          min: 1,
          max: 100,
          className: "text-center text-2xl font-bold"
        }
      ) }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Button,
        {
          variant: "secondary",
          size: "lg",
          onClick: () => onChange(Math.min(100, quantity + 1)),
          disabled: quantity >= 100,
          children: /* @__PURE__ */ jsxRuntimeExports.jsx(Plus, { className: "w-5 h-5" })
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-center text-sm", style: { color: "var(--color-text-tertiary)" }, children: [
      quantity,
      " batch",
      quantity > 1 ? "es" : "",
      " will be created"
    ] })
  ] });
}
function ReviewStep({
  sequenceName,
  sequenceDetail,
  stepOrder,
  parameters,
  quantity
}) {
  const enabledSteps = stepOrder.filter((s) => s.enabled);
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-medium mb-2", style: { color: "var(--color-text-primary)" }, children: "Review Configuration" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mb-4", style: { color: "var(--color-text-secondary)" }, children: "Please review the batch configuration before creating." })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "text-sm font-medium mb-2", style: { color: "var(--color-text-secondary)" }, children: "Sequence" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: [
          (sequenceDetail == null ? void 0 : sequenceDetail.displayName) || sequenceName,
          " (v",
          sequenceDetail == null ? void 0 : sequenceDetail.version,
          ")"
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("h4", { className: "text-sm font-medium mb-2", style: { color: "var(--color-text-secondary)" }, children: [
          "Steps (",
          enabledSteps.length,
          " enabled)"
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex flex-wrap gap-2", children: enabledSteps.map((step, index) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "span",
          {
            className: "px-2 py-1 rounded text-sm",
            style: { backgroundColor: "var(--color-bg-tertiary)", color: "var(--color-text-primary)" },
            children: [
              index + 1,
              ". ",
              step.displayName || step.name
            ]
          },
          step.name
        )) })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "text-sm font-medium mb-2", style: { color: "var(--color-text-secondary)" }, children: "Parameters" }),
        Object.keys(parameters).length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: "No parameters configured" }) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid grid-cols-2 md:grid-cols-3 gap-2 text-sm", children: Object.entries(parameters).map(([key, value]) => /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { style: { color: "var(--color-text-tertiary)" }, children: [
            key,
            ":"
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "ml-1 font-mono", style: { color: "var(--color-text-primary)" }, children: String(value) })
        ] }, key)) })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 bg-brand-500/10 rounded-lg border border-brand-500/30", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "text-sm font-medium text-brand-400 mb-2", children: "Batch Quantity" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: [
          quantity,
          " ",
          /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-base font-normal", style: { color: "var(--color-text-secondary)" }, children: [
            "batch",
            quantity > 1 ? "es" : ""
          ] })
        ] })
      ] })
    ] })
  ] });
}
function BatchStatisticsPanel({ batches: batches2, statistics }) {
  const totalStats = {
    total: 0,
    pass: 0,
    fail: 0,
    passRate: 0
  };
  statistics.forEach((stats) => {
    totalStats.total += stats.total;
    totalStats.pass += stats.passCount;
    totalStats.fail += stats.fail;
  });
  if (totalStats.total > 0) {
    totalStats.passRate = totalStats.pass / totalStats.total;
  }
  const statusCounts = {
    running: batches2.filter((b) => b.status === "running" || b.status === "starting").length,
    idle: batches2.filter((b) => b.status === "idle").length,
    completed: batches2.filter((b) => b.status === "completed").length,
    error: batches2.filter((b) => b.status === "error").length
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      StatCard,
      {
        icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Layers, { className: "w-5 h-5" }),
        label: "Total Executions",
        value: totalStats.total,
        color: "text-zinc-400",
        bgColor: "bg-zinc-700/50"
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      StatCard,
      {
        icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-5 h-5" }),
        label: "Passed",
        value: totalStats.pass,
        color: "text-green-500",
        bgColor: "bg-green-500/10"
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      StatCard,
      {
        icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-5 h-5" }),
        label: "Failed",
        value: totalStats.fail,
        color: "text-red-500",
        bgColor: "bg-red-500/10"
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      StatCard,
      {
        icon: /* @__PURE__ */ jsxRuntimeExports.jsx(TrendingUp, { className: "w-5 h-5" }),
        label: "Pass Rate",
        value: totalStats.total > 0 ? `${(totalStats.passRate * 100).toFixed(1)}%` : "-",
        color: totalStats.passRate >= 0.9 ? "text-green-500" : totalStats.passRate >= 0.7 ? "text-yellow-500" : totalStats.passRate > 0 ? "text-red-500" : "text-zinc-400",
        bgColor: totalStats.passRate >= 0.9 ? "bg-green-500/10" : totalStats.passRate >= 0.7 ? "bg-yellow-500/10" : totalStats.passRate > 0 ? "bg-red-500/10" : "bg-zinc-700/50"
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      StatCard,
      {
        icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Activity, { className: "w-5 h-5" }),
        label: "Running",
        value: statusCounts.running,
        color: "text-brand-500",
        bgColor: "bg-brand-500/10",
        subtitle: `${batches2.length} total batches`
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mb-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-5 h-5", style: { color: "var(--color-text-secondary)" } }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: "Batch Status" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(StatusDot, { color: "bg-brand-500", value: statusCounts.running, label: "Running" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(StatusDot, { color: "bg-zinc-500", value: statusCounts.idle, label: "Idle" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(StatusDot, { color: "bg-green-500", value: statusCounts.completed, label: "Done" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(StatusDot, { color: "bg-red-500", value: statusCounts.error, label: "Error" })
      ] })
    ] })
  ] });
}
function StatCard({
  icon,
  label,
  value,
  color,
  bgColor,
  subtitle
}) {
  const isNeutral = bgColor === "bg-zinc-700/50";
  const bgStyle = isNeutral ? { backgroundColor: "var(--color-bg-tertiary)", borderColor: "var(--color-border-default)" } : { borderColor: "var(--color-border-default)" };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: `p-4 rounded-lg border ${isNeutral ? "" : bgColor}`, style: bgStyle, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: `flex items-center gap-2 mb-2 ${color}`, children: [
      icon,
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: label })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: `text-2xl font-bold ${color}`, children: value }),
    subtitle && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs mt-1", style: { color: "var(--color-text-tertiary)" }, children: subtitle })
  ] });
}
function StatusDot({
  color,
  value,
  label
}) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1", title: label, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: `w-2 h-2 rounded-full ${color}` }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: value })
  ] });
}
function BatchesPage() {
  const navigate = useNavigate();
  const { data: batches2, isLoading: batchesLoading } = useBatchList();
  const { data: sequences } = useSequenceList();
  const { data: allStatistics } = useAllBatchStatistics();
  const { subscribe, isConnected } = useWebSocket();
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  const isServerConnected = isConnected && websocketStatus === "connected";
  const batchesMap = useBatchStore((state) => state.batches);
  const batchesVersion = useBatchStore((state) => state.batchesVersion);
  const batchStatistics = useBatchStore((state) => state.batchStatistics);
  const setAllBatchStatistics = useBatchStore((state) => state.setAllBatchStatistics);
  const isWizardOpen = useBatchStore((state) => state.isWizardOpen);
  const openWizard = useBatchStore((state) => state.openWizard);
  const closeWizard = useBatchStore((state) => state.closeWizard);
  reactExports.useEffect(() => {
    if (allStatistics) {
      setAllBatchStatistics(allStatistics);
    }
  }, [allStatistics, setAllBatchStatistics]);
  const storeBatches = reactExports.useMemo(() => {
    const arr = Array.from(batchesMap.values());
    console.log(`[BatchesPage] storeBatches recalc: version=${batchesVersion}, size=${arr.length}`, arr.map((b) => `${b.id.slice(0, 8)}:${b.status}`));
    return arr;
  }, [batchesMap, batchesVersion]);
  const createBatches2 = useCreateBatches();
  reactExports.useEffect(() => {
    if (batches2 && batches2.length > 0) {
      const batchIds = batches2.map((b) => b.id);
      subscribe(batchIds);
    }
  }, [batches2, subscribe]);
  const displayBatches = storeBatches.length > 0 ? storeBatches : batches2 ?? [];
  const handleSelectBatch = (id) => {
    navigate(getBatchDetailRoute(id));
  };
  const handleCreateBatches = async (request) => {
    await createBatches2.mutateAsync(request);
    closeWizard();
  };
  const getSequenceDetail = reactExports.useCallback(async (name) => {
    return getSequence(name);
  }, []);
  if (batchesLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingOverlay, { message: "Loading batches..." });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Layers, { className: "w-6 h-6 text-brand-500" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: "Batches" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        !isServerConnected && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 px-3 py-1.5 rounded-md bg-amber-500/10 border border-amber-500/30", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(WifiOff, { className: "w-4 h-4 text-amber-500" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm text-amber-500", children: "Server disconnected" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          Button,
          {
            variant: "primary",
            onClick: openWizard,
            disabled: !isServerConnected,
            title: !isServerConnected ? "Server connection required to create batches" : void 0,
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Plus, { className: "w-4 h-4 mr-2" }),
              "Create Batch"
            ]
          }
        )
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(BatchStatisticsPanel, { batches: displayBatches, statistics: batchStatistics }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      BatchList,
      {
        batches: displayBatches,
        statistics: batchStatistics,
        onSelect: handleSelectBatch
      },
      `batch-list-${batchesVersion}`
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      CreateBatchWizard,
      {
        isOpen: isWizardOpen,
        onClose: closeWizard,
        onSubmit: handleCreateBatches,
        sequences: sequences ?? [],
        getSequenceDetail,
        isSubmitting: createBatches2.isPending
      }
    )
  ] });
}
const MIN_PANEL_WIDTH = 280;
const MAX_PANEL_WIDTH = 600;
const DEFAULT_PANEL_WIDTH = 380;
const useDebugPanelStore = create()(
  persist(
    (set) => ({
      // Initial state
      isCollapsed: false,
      panelWidth: DEFAULT_PANEL_WIDTH,
      activeTab: "logs",
      selectedStep: null,
      logLevel: null,
      searchQuery: "",
      autoScroll: true,
      // Actions
      toggleCollapsed: () => set((state) => ({ isCollapsed: !state.isCollapsed })),
      setCollapsed: (isCollapsed) => set({ isCollapsed }),
      setPanelWidth: (width) => set({ panelWidth: Math.min(MAX_PANEL_WIDTH, Math.max(MIN_PANEL_WIDTH, width)) }),
      setActiveTab: (activeTab) => set({ activeTab }),
      setSelectedStep: (selectedStep) => set({ selectedStep }),
      setLogLevel: (logLevel) => set({ logLevel }),
      setSearchQuery: (searchQuery) => set({ searchQuery }),
      setAutoScroll: (autoScroll) => set({ autoScroll }),
      clearFilters: () => set({
        selectedStep: null,
        logLevel: null,
        searchQuery: ""
      })
    }),
    {
      name: "debug-panel-state",
      partialize: (state) => ({
        // Only persist these fields
        isCollapsed: state.isCollapsed,
        panelWidth: state.panelWidth,
        activeTab: state.activeTab,
        autoScroll: state.autoScroll
      })
    }
  )
);
function SplitLayout({
  children,
  panel,
  panelWidth,
  isCollapsed,
  onResize,
  onToggle,
  minWidth = 280,
  maxWidth = 600,
  panelTitle = "Details"
}) {
  const [isResizing, setIsResizing] = reactExports.useState(false);
  const containerRef = reactExports.useRef(null);
  const startXRef = reactExports.useRef(0);
  const startWidthRef = reactExports.useRef(0);
  const handleMouseDown = reactExports.useCallback(
    (e) => {
      e.preventDefault();
      setIsResizing(true);
      startXRef.current = e.clientX;
      startWidthRef.current = panelWidth;
    },
    [panelWidth]
  );
  const handleMouseMove = reactExports.useCallback(
    (e) => {
      if (!isResizing) return;
      const delta = startXRef.current - e.clientX;
      const newWidth = Math.min(maxWidth, Math.max(minWidth, startWidthRef.current + delta));
      onResize(newWidth);
    },
    [isResizing, minWidth, maxWidth, onResize]
  );
  const handleMouseUp = reactExports.useCallback(() => {
    setIsResizing(false);
  }, []);
  reactExports.useEffect(() => {
    if (isResizing) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    }
    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [isResizing, handleMouseMove, handleMouseUp]);
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { ref: containerRef, className: "flex h-full w-full overflow-hidden", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "flex-1 overflow-auto transition-all duration-200",
        style: {
          marginRight: isCollapsed ? 0 : panelWidth
        },
        children
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      "button",
      {
        onClick: onToggle,
        className: "fixed z-40 p-2 rounded-l-lg border-l border-t border-b transition-all duration-200 hover:bg-zinc-700",
        style: {
          backgroundColor: "var(--color-bg-secondary)",
          borderColor: "var(--color-border-default)",
          right: isCollapsed ? 0 : panelWidth,
          top: "50%",
          transform: "translateY(-50%)"
        },
        title: isCollapsed ? "Open debug panel" : "Close panel",
        children: isCollapsed ? /* @__PURE__ */ jsxRuntimeExports.jsx(PanelRightOpen, { className: "w-5 h-5", style: { color: "var(--color-text-secondary)" } }) : /* @__PURE__ */ jsxRuntimeExports.jsx(PanelRightClose, { className: "w-5 h-5", style: { color: "var(--color-text-secondary)" } })
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: `fixed right-0 top-[60px] h-[calc(100vh-60px)] flex flex-col border-l transition-transform duration-200 z-30 ${isCollapsed ? "translate-x-full" : "translate-x-0"}`,
        style: {
          width: panelWidth,
          backgroundColor: "var(--color-bg-secondary)",
          borderColor: "var(--color-border-default)"
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "div",
            {
              onMouseDown: handleMouseDown,
              className: `absolute left-0 top-0 h-full w-1 cursor-col-resize transition-colors ${isResizing ? "bg-brand-500" : "hover:bg-brand-500/50"}`,
              style: { transform: "translateX(-50%)" }
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "div",
            {
              className: "flex items-center justify-center px-3 py-2 border-b shrink-0",
              style: { borderColor: "var(--color-border-default)" },
              children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: panelTitle })
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex-1 overflow-hidden", children: panel })
        ]
      }
    )
  ] });
}
const levelOptions = [
  { value: "", label: "All Levels" },
  { value: "debug", label: "Debug" },
  { value: "info", label: "Info" },
  { value: "warning", label: "Warning" },
  { value: "error", label: "Error" }
];
function LogFilters({ stepNames }) {
  const { selectedStep, logLevel, searchQuery, setSelectedStep, setLogLevel, setSearchQuery, clearFilters } = useDebugPanelStore();
  const stepOptions = [
    { value: "", label: "All Steps" },
    ...stepNames.map((name) => ({ value: name, label: name }))
  ];
  const hasActiveFilters = selectedStep || logLevel || searchQuery;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "flex flex-col gap-2 px-3 py-2 border-b",
      style: { borderColor: "var(--color-border-default)" },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Select,
            {
              value: selectedStep || "",
              onChange: (e) => setSelectedStep(e.target.value || null),
              className: "flex-1 text-xs",
              placeholder: "All Steps",
              options: stepOptions
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Select,
            {
              value: logLevel || "",
              onChange: (e) => setLogLevel(e.target.value || null),
              className: "flex-1 text-xs",
              placeholder: "All Levels",
              options: levelOptions
            }
          )
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Search,
            {
              className: "absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5",
              style: { color: "var(--color-text-tertiary)" }
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Input,
            {
              type: "text",
              value: searchQuery,
              onChange: (e) => setSearchQuery(e.target.value),
              placeholder: "Search logs...",
              className: "pl-7 pr-7 text-xs w-full"
            }
          ),
          hasActiveFilters && /* @__PURE__ */ jsxRuntimeExports.jsx(
            "button",
            {
              onClick: clearFilters,
              className: "absolute right-2 top-1/2 -translate-y-1/2 p-0.5 rounded hover:bg-zinc-700",
              title: "Clear filters",
              children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-3.5 h-3.5", style: { color: "var(--color-text-tertiary)" } })
            }
          )
        ] })
      ]
    }
  );
}
const levelConfig = {
  debug: {
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Bug, { className: "w-3 h-3" }),
    bgClass: "bg-zinc-500/10",
    textClass: "text-zinc-400",
    borderClass: "border-l-zinc-500",
    label: "DBG"
  },
  info: {
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Info, { className: "w-3 h-3" }),
    bgClass: "bg-blue-500/10",
    textClass: "text-blue-400",
    borderClass: "border-l-blue-500",
    label: "INF"
  },
  warning: {
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-3 h-3" }),
    bgClass: "bg-yellow-500/10",
    textClass: "text-yellow-400",
    borderClass: "border-l-yellow-500",
    label: "WRN"
  },
  error: {
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleAlert, { className: "w-3 h-3" }),
    bgClass: "bg-red-500/10",
    textClass: "text-red-400",
    borderClass: "border-l-red-500",
    label: "ERR"
  }
};
function formatTimestamp(date) {
  return date.toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
}
function LogEntryRow({ log: log2, onClick }) {
  const config = levelConfig[log2.level];
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      onClick,
      className: `flex items-start gap-1.5 px-2 py-1 text-xs font-mono ${config.bgClass} border-l-2 ${config.borderClass} cursor-pointer hover:bg-zinc-800/50`,
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-zinc-500 flex-shrink-0 text-[10px]", children: formatTimestamp(log2.timestamp) }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: `flex items-center gap-0.5 flex-shrink-0 ${config.textClass}`, children: [
          config.icon,
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-[10px]", children: config.label })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: `flex-1 break-all text-[11px] leading-relaxed ${config.textClass}`, children: log2.message })
      ]
    }
  );
}
function LogEntryList({ batchId }) {
  const logs = useLogStore((s) => s.logs);
  const { selectedStep, logLevel, searchQuery, autoScroll, setAutoScroll } = useDebugPanelStore();
  const containerRef = reactExports.useRef(null);
  const prevLogsLengthRef = reactExports.useRef(logs.length);
  const filteredLogs = reactExports.useMemo(() => {
    return logs.filter((log2) => {
      if (log2.batchId !== batchId) return false;
      if (logLevel && log2.level !== logLevel) return false;
      if (searchQuery && !log2.message.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }
      if (selectedStep && !log2.message.toLowerCase().includes(selectedStep.toLowerCase())) {
        return false;
      }
      return true;
    });
  }, [logs, batchId, selectedStep, logLevel, searchQuery]);
  reactExports.useEffect(() => {
    if (autoScroll && containerRef.current && logs.length > prevLogsLengthRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
    prevLogsLengthRef.current = logs.length;
  }, [logs.length, autoScroll]);
  const handleScroll = reactExports.useCallback(() => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    if (isAtBottom !== autoScroll) {
      setAutoScroll(isAtBottom);
    }
  }, [autoScroll, setAutoScroll]);
  const scrollToBottom = () => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
      setAutoScroll(true);
    }
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative flex flex-col h-full", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "flex items-center justify-between px-2 py-1 text-[10px] border-b",
        style: {
          color: "var(--color-text-tertiary)",
          borderColor: "var(--color-border-subtle)",
          backgroundColor: "var(--color-bg-tertiary)"
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
            filteredLogs.length,
            " entries"
          ] }),
          !autoScroll && /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-yellow-500", children: "Scroll paused" })
        ]
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        ref: containerRef,
        onScroll: handleScroll,
        className: "flex-1 overflow-y-auto",
        style: { backgroundColor: "var(--color-bg-tertiary)" },
        children: filteredLogs.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col items-center justify-center py-8", style: { color: "var(--color-text-tertiary)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(FileText, { className: "w-6 h-6 mb-2 opacity-50" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs", children: "No log entries" }),
          (selectedStep || logLevel || searchQuery) && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[10px] mt-1", children: "Try adjusting filters" })
        ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "divide-y", style: { borderColor: "var(--color-border-subtle)" }, children: filteredLogs.map((log2) => /* @__PURE__ */ jsxRuntimeExports.jsx(LogEntryRow, { log: log2 }, log2.id)) })
      }
    ),
    !autoScroll && filteredLogs.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "absolute bottom-2 right-2", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "secondary", size: "sm", onClick: scrollToBottom, className: "shadow-lg text-xs px-2 py-1", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(ArrowDown, { className: "w-3 h-3 mr-1" }),
      "Latest"
    ] }) })
  ] });
}
function StepRow$1({ step, isSelected, isExpanded, onToggle, onClick }) {
  const [copied, setCopied] = reactExports.useState(false);
  const handleCopy = async (e) => {
    e.stopPropagation();
    if (step.result) {
      await navigator.clipboard.writeText(JSON.stringify(step.result, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2e3);
    }
  };
  const hasData = step.result && Object.keys(step.result).length > 0;
  const hasError = !!step.error;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: `border-b transition-colors ${isSelected ? "bg-brand-500/10" : ""}`,
      style: { borderColor: "var(--color-border-subtle)" },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            onClick: () => {
              onClick();
              if (hasData || hasError) onToggle();
            },
            className: `flex items-center gap-2 px-2 py-1.5 cursor-pointer hover:bg-zinc-800/50 ${hasData || hasError ? "" : "opacity-60"}`,
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-4 h-4 flex items-center justify-center", children: (hasData || hasError) && (isExpanded ? /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronDown, { className: "w-3.5 h-3.5", style: { color: "var(--color-text-tertiary)" } }) : /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronRight, { className: "w-3.5 h-3.5", style: { color: "var(--color-text-tertiary)" } })) }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "span",
                {
                  className: "w-5 text-center text-xs font-mono",
                  style: { color: "var(--color-text-tertiary)" },
                  children: step.order
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "flex-1 text-xs font-medium truncate", style: { color: "var(--color-text-primary)" }, children: step.name }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
                step.duration != null && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  "span",
                  {
                    className: "flex items-center gap-0.5 text-[10px] font-mono",
                    style: { color: "var(--color-text-tertiary)" },
                    children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-3 h-3" }),
                      step.duration.toFixed(2),
                      "s"
                    ]
                  }
                ),
                step.status === "completed" && /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: step.pass ? "text-green-500" : "text-red-500", children: step.pass ? /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-3.5 h-3.5" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-3.5 h-3.5" }) }),
                step.status === "running" && /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge, { status: "running", size: "sm" }),
                step.status === "failed" && /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-3.5 h-3.5 text-red-500" }),
                hasData && /* @__PURE__ */ jsxRuntimeExports.jsx("span", { title: "Has data", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Database, { className: "w-3 h-3", style: { color: "var(--color-text-tertiary)" } }) })
              ] })
            ]
          }
        ),
        isExpanded && (hasData || hasError) && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "px-2 py-2 ml-6", style: { backgroundColor: "var(--color-bg-tertiary)" }, children: [
          hasError && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-2 p-2 rounded bg-red-500/10 border border-red-500/30", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1 text-xs text-red-400 mb-1", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(CircleAlert, { className: "w-3 h-3" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", children: "Error" })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-red-300 font-mono break-all", children: step.error })
          ] }),
          hasData && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-1", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-[10px] font-medium", style: { color: "var(--color-text-tertiary)" }, children: "Measurements" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "button",
                {
                  onClick: handleCopy,
                  className: "p-1 rounded hover:bg-zinc-700 transition-colors",
                  title: "Copy JSON",
                  children: copied ? /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "w-3 h-3 text-green-500" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Copy, { className: "w-3 h-3", style: { color: "var(--color-text-tertiary)" } })
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-0.5", children: Object.entries(step.result || {}).map(([key, value]) => /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-start gap-2 text-[11px] font-mono", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-brand-400 flex-shrink-0", children: [
                key,
                ":"
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-zinc-300 break-all", children: formatValue(value) })
            ] }, key)) })
          ] })
        ] })
      ]
    }
  );
}
function formatValue(value) {
  if (value === null) return "null";
  if (value === void 0) return "undefined";
  if (typeof value === "object") {
    return JSON.stringify(value, null, 2);
  }
  if (typeof value === "number") {
    if (Number.isInteger(value)) return value.toString();
    return value.toFixed(4);
  }
  return String(value);
}
function StepDataViewer({ steps }) {
  const { selectedStep, setSelectedStep } = useDebugPanelStore();
  const [expandedSteps, setExpandedSteps] = reactExports.useState(/* @__PURE__ */ new Set());
  const toggleExpanded = (stepName) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(stepName)) {
        next.delete(stepName);
      } else {
        next.add(stepName);
      }
      return next;
    });
  };
  if (steps.length === 0) {
    return /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "flex flex-col items-center justify-center py-8",
        style: { color: "var(--color-text-tertiary)" },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Database, { className: "w-6 h-6 mb-2 opacity-50" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs", children: "No step data available" })
        ]
      }
    );
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex flex-col h-full overflow-y-auto", children: steps.map((step) => /* @__PURE__ */ jsxRuntimeExports.jsx(
    StepRow$1,
    {
      step,
      isSelected: selectedStep === step.name,
      isExpanded: expandedSteps.has(step.name),
      onToggle: () => toggleExpanded(step.name),
      onClick: () => setSelectedStep(selectedStep === step.name ? null : step.name)
    },
    `${step.order}-${step.name}`
  )) });
}
function isBatchDetail$3(batch) {
  return batch !== null && typeof batch === "object" && "parameters" in batch;
}
function BatchConfigEditor({ batchId, isRunning }) {
  const { data: batch } = useBatch(batchId);
  const { data: processes = [], isLoading: processesLoading } = useProcesses();
  const updateBatch2 = useUpdateBatch();
  const [selectedProcessId, setSelectedProcessId] = reactExports.useState();
  const [headerId, setHeaderId] = reactExports.useState();
  const [hasChanges, setHasChanges] = reactExports.useState(false);
  reactExports.useEffect(() => {
    if (batch && isBatchDetail$3(batch)) {
      setSelectedProcessId(batch.processId);
      setHeaderId(batch.headerId);
      setHasChanges(false);
    }
  }, [batch]);
  const handleProcessChange = (processId) => {
    setSelectedProcessId(processId);
    setHasChanges(true);
  };
  const handleHeaderIdChange = (value) => {
    const parsed = parseInt(value, 10);
    setHeaderId(isNaN(parsed) ? void 0 : parsed);
    setHasChanges(true);
  };
  const handleSave = async () => {
    if (!batchId) return;
    await updateBatch2.mutateAsync({ batchId, request: { processId: selectedProcessId, headerId } });
    setHasChanges(false);
  };
  const handleReset = () => {
    if (batch && isBatchDetail$3(batch)) {
      setSelectedProcessId(batch.processId);
      setHeaderId(batch.headerId);
      setHasChanges(false);
    }
  };
  const selectedProcess = reactExports.useMemo(() => {
    return processes.find((p) => p.processNumber === selectedProcessId);
  }, [processes, selectedProcessId]);
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col h-full", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "flex items-center justify-between px-3 py-2 border-b shrink-0",
        style: { borderColor: "var(--color-border-default)" },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Settings, { className: "w-4 h-4", style: { color: "var(--color-text-tertiary)" } }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: "Process Configuration" })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1", children: [
            hasChanges && /* @__PURE__ */ jsxRuntimeExports.jsx(
              Button,
              {
                variant: "ghost",
                size: "sm",
                onClick: handleReset,
                disabled: isRunning,
                title: "Reset changes",
                className: "p-1",
                children: /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "w-3.5 h-3.5" })
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              Button,
              {
                variant: "primary",
                size: "sm",
                onClick: handleSave,
                disabled: !hasChanges || isRunning || updateBatch2.isPending,
                isLoading: updateBatch2.isPending,
                title: "Save changes",
                className: "px-2 py-1 text-xs",
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Save, { className: "w-3 h-3 mr-1" }),
                  "Save"
                ]
              }
            )
          ] })
        ]
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 overflow-auto p-3 space-y-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "label",
          {
            className: "block text-xs font-medium",
            style: { color: "var(--color-text-secondary)" },
            children: "MES Process (Start/Complete)"
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "select",
          {
            value: selectedProcessId ?? "",
            onChange: (e) => handleProcessChange(Number(e.target.value)),
            disabled: isRunning || processesLoading,
            className: "w-full text-sm rounded px-3 py-2 border outline-none transition-colors disabled:opacity-50",
            style: {
              backgroundColor: "var(--color-bg-tertiary)",
              borderColor: "var(--color-border-default)",
              color: "var(--color-text-primary)"
            },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "", children: "Select process..." }),
              processes.map((p) => /* @__PURE__ */ jsxRuntimeExports.jsxs("option", { value: p.processNumber, children: [
                "P",
                p.processNumber,
                ". ",
                p.processNameKo
              ] }, p.id))
            ]
          }
        ),
        selectedProcess && /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: [
          "Code: ",
          selectedProcess.processCode,
          " | ",
          selectedProcess.processNameEn
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "label",
          {
            className: "block text-xs font-medium",
            style: { color: "var(--color-text-secondary)" },
            children: "Process Header ID"
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "input",
          {
            type: "number",
            value: headerId ?? "",
            onChange: (e) => handleHeaderIdChange(e.target.value),
            disabled: isRunning,
            placeholder: "Enter header ID...",
            className: "w-full text-sm rounded px-3 py-2 border outline-none transition-colors disabled:opacity-50",
            style: {
              backgroundColor: "var(--color-bg-tertiary)",
              borderColor: "var(--color-border-default)",
              color: "var(--color-text-primary)"
            }
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Unique ID to distinguish batches (e.g., 1, 2, 3, 4...)" })
      ] }),
      isRunning && /* @__PURE__ */ jsxRuntimeExports.jsx(
        "div",
        {
          className: "text-xs p-2 rounded",
          style: {
            backgroundColor: "rgba(var(--color-brand-rgb), 0.1)",
            color: "var(--color-brand-500)"
          },
          children: "Process selection is disabled while the batch is running."
        }
      )
    ] })
  ] });
}
function isBatchDetail$2(batch) {
  return batch !== null && typeof batch === "object" && "parameters" in batch;
}
function ParametersEditor({ batchId, isRunning }) {
  const { data: batch } = useBatch(batchId);
  const updateBatch2 = useUpdateBatch();
  const [editedParams, setEditedParams] = reactExports.useState({});
  const [hasChanges, setHasChanges] = reactExports.useState(false);
  const [searchQuery, setSearchQuery] = reactExports.useState("");
  reactExports.useEffect(() => {
    if (batch && isBatchDetail$2(batch)) {
      setEditedParams(batch.parameters || {});
      setHasChanges(false);
    }
  }, [batch]);
  const currentParams = reactExports.useMemo(() => {
    if (batch && isBatchDetail$2(batch)) {
      return batch.parameters || {};
    }
    return {};
  }, [batch]);
  const filteredParams = reactExports.useMemo(() => {
    if (!searchQuery.trim()) {
      return Object.entries(editedParams);
    }
    const query = searchQuery.toLowerCase();
    return Object.entries(editedParams).filter(
      ([key, value]) => key.toLowerCase().includes(query) || String(value ?? "").toLowerCase().includes(query)
    );
  }, [editedParams, searchQuery]);
  const handleParamChange = (key, value) => {
    const newParams = { ...editedParams };
    if (value === "true") {
      newParams[key] = true;
    } else if (value === "false") {
      newParams[key] = false;
    } else if (!isNaN(Number(value)) && value !== "") {
      newParams[key] = Number(value);
    } else {
      newParams[key] = value;
    }
    setEditedParams(newParams);
    setHasChanges(true);
  };
  const handleSave = async () => {
    if (!batchId) return;
    if (JSON.stringify(editedParams) !== JSON.stringify(currentParams)) {
      await updateBatch2.mutateAsync({ batchId, request: { parameters: editedParams } });
      setHasChanges(false);
    }
  };
  const handleReset = () => {
    if (batch && isBatchDetail$2(batch)) {
      setEditedParams(batch.parameters || {});
      setHasChanges(false);
    }
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col h-full", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "flex items-center justify-between px-3 py-2 border-b shrink-0",
        style: { borderColor: "var(--color-border-default)" },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(SlidersVertical, { className: "w-4 h-4", style: { color: "var(--color-text-tertiary)" } }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: "Parameters" }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: [
              "(",
              filteredParams.length,
              "/",
              Object.keys(editedParams).length,
              ")"
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1", children: [
            hasChanges && /* @__PURE__ */ jsxRuntimeExports.jsx(
              Button,
              {
                variant: "ghost",
                size: "sm",
                onClick: handleReset,
                disabled: isRunning,
                title: "Reset changes",
                className: "p-1",
                children: /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "w-3.5 h-3.5" })
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              Button,
              {
                variant: "primary",
                size: "sm",
                onClick: handleSave,
                disabled: !hasChanges || isRunning || updateBatch2.isPending,
                isLoading: updateBatch2.isPending,
                title: "Save changes",
                className: "px-2 py-1 text-xs",
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Save, { className: "w-3 h-3 mr-1" }),
                  "Save"
                ]
              }
            )
          ] })
        ]
      }
    ),
    Object.keys(editedParams).length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "px-3 py-2 border-b shrink-0", style: { borderColor: "var(--color-border-default)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Search,
        {
          className: "absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5",
          style: { color: "var(--color-text-tertiary)" }
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "input",
        {
          type: "text",
          value: searchQuery,
          onChange: (e) => setSearchQuery(e.target.value),
          placeholder: "Search parameters...",
          className: "w-full text-xs rounded px-2 py-1.5 pl-7 pr-7 border outline-none transition-colors",
          style: {
            backgroundColor: "var(--color-bg-tertiary)",
            borderColor: "var(--color-border-default)",
            color: "var(--color-text-primary)"
          }
        }
      ),
      searchQuery && /* @__PURE__ */ jsxRuntimeExports.jsx(
        "button",
        {
          onClick: () => setSearchQuery(""),
          className: "absolute right-2 top-1/2 -translate-y-1/2 p-0.5 rounded hover:bg-black/10",
          title: "Clear search",
          children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-3 h-3", style: { color: "var(--color-text-tertiary)" } })
        }
      )
    ] }) }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 overflow-auto p-3", children: [
      Object.keys(editedParams).length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs italic", style: { color: "var(--color-text-tertiary)" }, children: "No parameters configured for this batch." }) : filteredParams.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs italic", style: { color: "var(--color-text-tertiary)" }, children: [
        'No parameters match "',
        searchQuery,
        '"'
      ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2", children: filteredParams.map(([key, value]) => /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "label",
          {
            className: "text-xs w-1/3 truncate",
            style: { color: "var(--color-text-secondary)" },
            title: key,
            children: key
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "input",
          {
            type: "text",
            value: String(value ?? ""),
            onChange: (e) => handleParamChange(key, e.target.value),
            disabled: isRunning,
            className: "flex-1 text-xs rounded px-2 py-1 border outline-none transition-colors disabled:opacity-50",
            style: {
              backgroundColor: "var(--color-bg-tertiary)",
              borderColor: "var(--color-border-default)",
              color: "var(--color-text-primary)"
            }
          }
        )
      ] }, key)) }),
      isRunning && /* @__PURE__ */ jsxRuntimeExports.jsx(
        "div",
        {
          className: "text-xs p-2 rounded mt-4",
          style: {
            backgroundColor: "rgba(var(--color-brand-rgb), 0.1)",
            color: "var(--color-brand-500)"
          },
          children: "Parameter editing is disabled while the batch is running."
        }
      )
    ] })
  ] });
}
function TabButton$1({ label, icon, isActive, onClick }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "button",
    {
      onClick,
      className: `flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-t transition-colors ${isActive ? "bg-zinc-800 text-zinc-100 border-b-2 border-brand-500" : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"}`,
      children: [
        icon,
        label
      ]
    }
  );
}
function DebugLogPanel({ batchId, steps, isRunning = false }) {
  const { activeTab, setActiveTab, selectedStep, logLevel, searchQuery } = useDebugPanelStore();
  const logs = useLogStore((s) => s.logs);
  const clearLogs = useLogStore((s) => s.clearLogs);
  const stepNames = reactExports.useMemo(() => {
    return steps.map((s) => s.name);
  }, [steps]);
  const filteredLogs = reactExports.useMemo(() => {
    return logs.filter((log2) => {
      if (log2.batchId !== batchId) return false;
      if (logLevel && log2.level !== logLevel) return false;
      if (searchQuery && !log2.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      if (selectedStep && !log2.message.toLowerCase().includes(selectedStep.toLowerCase())) return false;
      return true;
    });
  }, [logs, batchId, logLevel, searchQuery, selectedStep]);
  const handleExportLogs = () => {
    const content = filteredLogs.map((log2) => {
      const time = log2.timestamp.toLocaleTimeString("en-US", {
        hour12: false,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
      });
      return `${time} [${log2.level.toUpperCase()}] ${log2.message}`;
    }).join("\n");
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `debug-log-${batchId}-${(/* @__PURE__ */ new Date()).toISOString().slice(0, 19).replace(/:/g, "-")}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };
  const handleExportData = () => {
    const data = steps.map((step) => ({
      order: step.order,
      name: step.name,
      status: step.status,
      pass: step.pass,
      duration: step.duration,
      result: step.result,
      error: step.error
    }));
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `step-data-${batchId}-${(/* @__PURE__ */ new Date()).toISOString().slice(0, 19).replace(/:/g, "-")}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col h-full", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "flex items-center justify-between px-2 py-1 border-b",
        style: {
          backgroundColor: "var(--color-bg-tertiary)",
          borderColor: "var(--color-border-default)"
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              TabButton$1,
              {
                tab: "logs",
                label: "Logs",
                icon: /* @__PURE__ */ jsxRuntimeExports.jsx(FileText, { className: "w-3.5 h-3.5" }),
                isActive: activeTab === "logs",
                onClick: () => setActiveTab("logs")
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              TabButton$1,
              {
                tab: "data",
                label: "Data",
                icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Database, { className: "w-3.5 h-3.5" }),
                isActive: activeTab === "data",
                onClick: () => setActiveTab("data")
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              TabButton$1,
              {
                tab: "params",
                label: "Params",
                icon: /* @__PURE__ */ jsxRuntimeExports.jsx(SlidersVertical, { className: "w-3.5 h-3.5" }),
                isActive: activeTab === "params",
                onClick: () => setActiveTab("params")
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              TabButton$1,
              {
                tab: "config",
                label: "Config",
                icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Settings, { className: "w-3.5 h-3.5" }),
                isActive: activeTab === "config",
                onClick: () => setActiveTab("config")
              }
            )
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Button,
              {
                variant: "ghost",
                size: "sm",
                onClick: activeTab === "logs" ? handleExportLogs : handleExportData,
                disabled: activeTab === "logs" ? filteredLogs.length === 0 : steps.length === 0,
                title: "Export",
                className: "p-1",
                children: /* @__PURE__ */ jsxRuntimeExports.jsx(Download, { className: "w-3.5 h-3.5" })
              }
            ),
            activeTab === "logs" && /* @__PURE__ */ jsxRuntimeExports.jsx(
              Button,
              {
                variant: "ghost",
                size: "sm",
                onClick: clearLogs,
                disabled: logs.length === 0,
                title: "Clear logs",
                className: "p-1",
                children: /* @__PURE__ */ jsxRuntimeExports.jsx(Trash2, { className: "w-3.5 h-3.5" })
              }
            )
          ] })
        ]
      }
    ),
    activeTab === "logs" && /* @__PURE__ */ jsxRuntimeExports.jsx(LogFilters, { stepNames }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 overflow-hidden", children: [
      activeTab === "logs" && /* @__PURE__ */ jsxRuntimeExports.jsx(LogEntryList, { batchId }),
      activeTab === "data" && /* @__PURE__ */ jsxRuntimeExports.jsx(StepDataViewer, { steps }),
      activeTab === "params" && /* @__PURE__ */ jsxRuntimeExports.jsx(ParametersEditor, { batchId, isRunning }),
      activeTab === "config" && /* @__PURE__ */ jsxRuntimeExports.jsx(BatchConfigEditor, { batchId, isRunning })
    ] })
  ] });
}
function WipInputModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
  batchName,
  errorMessage
}) {
  const [wipId, setWipId] = reactExports.useState("");
  const [localError, setLocalError] = reactExports.useState(null);
  const inputRef = reactExports.useRef(null);
  const error = errorMessage || localError;
  reactExports.useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);
  reactExports.useEffect(() => {
    if (!isOpen) {
      setWipId("");
      setLocalError(null);
    }
  }, [isOpen]);
  const handleSubmit = (e) => {
    e.preventDefault();
    setLocalError(null);
    const trimmedWipId = wipId.trim();
    if (!trimmedWipId) {
      setLocalError("WIP ID is required");
      return;
    }
    onSubmit(trimmedWipId);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsx(
    Modal,
    {
      isOpen,
      onClose,
      title: "Enter WIP ID",
      size: "sm",
      showCloseButton: !isLoading,
      children: /* @__PURE__ */ jsxRuntimeExports.jsxs("form", { onSubmit: handleSubmit, className: "space-y-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "p",
          {
            className: "text-sm",
            style: { color: "var(--color-text-secondary)" },
            children: [
              batchName && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "block mb-1", children: [
                "Starting sequence: ",
                /* @__PURE__ */ jsxRuntimeExports.jsx("strong", { style: { color: "var(--color-text-primary)" }, children: batchName })
              ] }),
              "Scan or enter the WIP barcode to start the process."
            ]
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Barcode,
              {
                className: "absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5",
                style: { color: "var(--color-text-tertiary)" }
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "input",
              {
                ref: inputRef,
                type: "text",
                value: wipId,
                onChange: (e) => setWipId(e.target.value),
                placeholder: "Enter or scan WIP ID",
                disabled: isLoading,
                className: "w-full pl-11 pr-4 py-3 text-sm rounded-lg border outline-none transition-colors disabled:opacity-50",
                style: {
                  backgroundColor: "var(--color-bg-primary)",
                  borderColor: error ? "var(--color-status-error)" : "var(--color-border-default)",
                  color: "var(--color-text-primary)"
                },
                onFocus: (e) => {
                  e.currentTarget.style.borderColor = "var(--color-brand-500)";
                },
                onBlur: (e) => {
                  e.currentTarget.style.borderColor = error ? "var(--color-status-error)" : "var(--color-border-default)";
                }
              }
            )
          ] }),
          error && /* @__PURE__ */ jsxRuntimeExports.jsx(
            "p",
            {
              className: "mt-1 text-xs",
              style: { color: "var(--color-status-error)" },
              children: error
            }
          )
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 pt-2", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Button,
            {
              type: "button",
              variant: "secondary",
              size: "md",
              onClick: onClose,
              disabled: isLoading,
              className: "flex-1",
              children: "Cancel"
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Button,
            {
              type: "submit",
              variant: "primary",
              size: "md",
              disabled: isLoading,
              className: "flex-1",
              children: isLoading ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-4 h-4 mr-2 animate-spin" }),
                "Starting..."
              ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-4 h-4 mr-2" }),
                "Start"
              ] })
            }
          )
        ] })
      ] })
    }
  );
}
const log = createLogger({ prefix: "BatchDetailPage" });
function isBatchDetail$1(batch) {
  return "parameters" in batch && "hardwareStatus" in batch;
}
function BatchDetailPage() {
  const { batchId } = useParams();
  const navigate = useNavigate();
  const { data: batch, isLoading } = useBatch(batchId ?? null);
  const { data: apiStatistics } = useBatchStatistics(batchId ?? null);
  const { subscribe } = useWebSocket();
  const getBatchStats = useBatchStore((state) => state.getBatchStats);
  const setBatchStatistics = useBatchStore((state) => state.setBatchStatistics);
  const startBatch2 = useStartBatch();
  const startSequence2 = useStartSequence();
  const stopSequence2 = useStopSequence();
  const stopBatch2 = useStopBatch();
  const deleteBatch2 = useDeleteBatch();
  const { isCollapsed, panelWidth, setPanelWidth, toggleCollapsed, setSelectedStep } = useDebugPanelStore();
  const { data: workflowConfig } = useWorkflowConfig();
  const [showWipModal, setShowWipModal] = reactExports.useState(false);
  const [wipError, setWipError] = reactExports.useState(null);
  reactExports.useEffect(() => {
    if (batchId) {
      log.debug(`useEffect: subscribing to batch ${batchId.slice(0, 8)}...`);
      subscribe([batchId]);
    }
  }, [batchId, subscribe]);
  reactExports.useEffect(() => {
    if (batchId && apiStatistics) {
      setBatchStatistics(batchId, apiStatistics);
    }
  }, [batchId, apiStatistics, setBatchStatistics]);
  const storeStatistics = reactExports.useMemo(() => {
    return batchId ? getBatchStats(batchId) : void 0;
  }, [batchId, getBatchStats]);
  const statistics = storeStatistics ?? apiStatistics;
  const steps = reactExports.useMemo(() => {
    var _a;
    if (!batch) return [];
    if (batch.steps && batch.steps.length > 0) {
      return batch.steps;
    }
    if (isBatchDetail$1(batch) && ((_a = batch.execution) == null ? void 0 : _a.steps)) {
      return batch.execution.steps;
    }
    return [];
  }, [batch]);
  const handleBack = () => {
    navigate(ROUTES.BATCHES);
  };
  const handleStartSequence = async () => {
    if (!batchId || !batch) {
      log.error("handleStartSequence: Missing batchId or batch");
      return;
    }
    if (workflowConfig == null ? void 0 : workflowConfig.enabled) {
      setShowWipModal(true);
      return;
    }
    await doStartSequence();
  };
  const doStartSequence = async (wipId, wipIntId) => {
    if (!batchId || !batch) {
      log.error("doStartSequence: Missing batchId or batch");
      return;
    }
    let batchWasStarted = false;
    try {
      log.debug("doStartSequence: Starting sequence for batch:", batchId, "status:", batch.status, "wipId:", wipId || "(none)");
      if (batch.status === "idle") {
        log.debug("doStartSequence: Starting batch first...");
        await startBatch2.mutateAsync(batchId);
        batchWasStarted = true;
        log.debug("doStartSequence: Batch started");
      }
      const request = wipId ? {
        parameters: { wip_id: wipId },
        wip_int_id: wipIntId
        // Skip lookup in worker if provided
      } : void 0;
      log.debug("doStartSequence: Starting sequence...");
      await startSequence2.mutateAsync({ batchId, request });
      log.debug("doStartSequence: Sequence started successfully");
    } catch (error) {
      log.error("doStartSequence: Error:", error);
      if (batchWasStarted) {
        log.debug("doStartSequence: Stopping batch due to sequence start failure...");
        try {
          await stopBatch2.mutateAsync(batchId);
          log.debug("doStartSequence: Batch stopped");
        } catch (stopError) {
          log.error("doStartSequence: Failed to stop batch:", stopError);
        }
      }
      throw error;
    }
  };
  const handleWipSubmit = async (wipId) => {
    setWipError(null);
    try {
      const processId = batch && isBatchDetail$1(batch) ? batch.processId : void 0;
      const validationResult = await validateWip(wipId, processId);
      if (!validationResult.valid) {
        setWipError(validationResult.message || `WIP '${wipId}' not found`);
        return;
      }
      if (validationResult.hasPassForProcess) {
        setWipError(validationResult.passWarningMessage || "이 WIP는 이미 해당 공정을 PASS했습니다.");
        return;
      }
      setShowWipModal(false);
      await doStartSequence(wipId, validationResult.intId);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : (error == null ? void 0 : error.message) || "Failed to validate WIP";
      if (showWipModal) {
        setWipError(errorMessage);
      } else {
        toast.error(errorMessage);
      }
    }
  };
  const handleWipModalClose = () => {
    setShowWipModal(false);
    setWipError(null);
  };
  const handleStopSequence = async () => {
    if (batchId) {
      await stopSequence2.mutateAsync(batchId);
      await stopBatch2.mutateAsync(batchId);
    }
  };
  const handleDeleteBatch = async () => {
    if (batchId && window.confirm("Are you sure you want to delete this batch?")) {
      await deleteBatch2.mutateAsync(batchId);
      navigate(ROUTES.BATCHES);
    }
  };
  if (isLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingOverlay, { message: "Loading batch details..." });
  }
  if (!batch) {
    return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-h-screen flex flex-col items-center justify-center", style: { backgroundColor: "var(--color-bg-primary)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(CircleAlert, { className: "w-16 h-16 mb-4", style: { color: "var(--color-text-tertiary)" } }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-lg mb-4", style: { color: "var(--color-text-tertiary)" }, children: "Batch not found" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "secondary", onClick: handleBack, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(ArrowLeft, { className: "w-4 h-4 mr-2" }),
        "Back to Batches"
      ] })
    ] });
  }
  const isRunning = batch.status === "running" || batch.status === "starting" || batch.status === "stopping";
  const canStart = batch.status === "idle" || batch.status === "completed" || batch.status === "error";
  const elapsedTime = isRunning ? batch.elapsed : batch.elapsed > 0 ? batch.elapsed : isBatchDetail$1(batch) && batch.execution && batch.execution.elapsed > 0 ? batch.execution.elapsed : (statistics == null ? void 0 : statistics.lastDuration) ?? 0;
  const progress = batch.progress ?? (isBatchDetail$1(batch) && batch.execution ? batch.execution.progress : 0);
  const getFinalVerdict = () => {
    if (batch.status === "running" || batch.status === "starting") {
      return { text: "In Progress", color: "text-brand-500", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-6 h-6 animate-spin" }) };
    }
    if (batch.status === "completed") {
      const hasFailed = steps.some((s) => !s.pass && s.status === "completed");
      if (hasFailed) {
        return { text: "FAIL", color: "text-red-500", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-6 h-6" }) };
      }
      return { text: "PASS", color: "text-green-500", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-6 h-6" }) };
    }
    if (batch.status === "error") {
      return { text: "ERROR", color: "text-red-500", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-6 h-6" }) };
    }
    return null;
  };
  const verdict = getFinalVerdict();
  const handleStepRowClick = (stepName) => {
    setSelectedStep(stepName);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    SplitLayout,
    {
      panel: /* @__PURE__ */ jsxRuntimeExports.jsx(DebugLogPanel, { batchId: batchId || "", steps, isRunning }),
      panelWidth,
      isCollapsed,
      onResize: setPanelWidth,
      onToggle: toggleCollapsed,
      panelTitle: "Batch Panel",
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-h-full p-6 space-y-6", style: { backgroundColor: "var(--color-bg-primary)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-4", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: handleBack, children: /* @__PURE__ */ jsxRuntimeExports.jsx(ArrowLeft, { className: "w-5 h-5" }) }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: batch.name }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: [
                  "ID: ",
                  batch.id
                ] })
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge, { status: batch.status }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "hidden md:flex items-center gap-4 ml-4 pl-4 border-l", style: { borderColor: "var(--color-border-default)" }, children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1.5 text-sm", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Runs:" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: (statistics == null ? void 0 : statistics.total) ?? 0 })
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1.5 text-sm", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-3.5 h-3.5 text-green-500" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium text-green-500", children: (statistics == null ? void 0 : statistics.passCount) ?? 0 })
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1.5 text-sm", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-3.5 h-3.5 text-red-500" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium text-red-500", children: (statistics == null ? void 0 : statistics.fail) ?? 0 })
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1.5 text-sm", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Rate:" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "font-medium text-brand-500", children: [
                    (((statistics == null ? void 0 : statistics.passRate) ?? 0) * 100).toFixed(0),
                    "%"
                  ] })
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1.5 text-sm", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-3.5 h-3.5", style: { color: "var(--color-text-tertiary)" } }),
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "font-mono", style: { color: "var(--color-text-secondary)" }, children: [
                    elapsedTime.toFixed(2),
                    "s"
                  ] })
                ] }),
                verdict && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: `flex items-center gap-1 font-bold ${verdict.color}`, children: [
                  verdict.icon,
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", children: verdict.text })
                ] })
              ] })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
              canStart && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                Button,
                {
                  variant: "primary",
                  onClick: handleStartSequence,
                  isLoading: startBatch2.isPending || startSequence2.isPending,
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-4 h-4 mr-2" }),
                    "Start Sequence"
                  ]
                }
              ),
              isRunning && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                Button,
                {
                  variant: "danger",
                  onClick: handleStopSequence,
                  isLoading: stopSequence2.isPending || stopBatch2.isPending,
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(Square, { className: "w-4 h-4 mr-2" }),
                    "Stop"
                  ]
                }
              ),
              !isRunning && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                Button,
                {
                  variant: "ghost",
                  onClick: handleDeleteBatch,
                  isLoading: deleteBatch2.isPending,
                  className: "text-red-500 hover:text-red-400 hover:bg-red-500/10",
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(Trash2, { className: "w-4 h-4 mr-2" }),
                    "Delete"
                  ]
                }
              )
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-lg p-4 border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-2", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: "Test Progress" }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: [
                Math.round(progress * 100),
                "%"
              ] })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              ProgressBar,
              {
                value: progress * 100,
                variant: batch.status === "completed" ? steps.every((s) => s.pass) ? "success" : "error" : "default"
              }
            ),
            batch.currentStep && isRunning && /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "mt-2 text-sm text-brand-400", children: [
              "Current Step: ",
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", children: batch.currentStep })
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-lg p-6 border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mb-4", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Package, { className: "w-5 h-5 text-brand-500" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: "Sequence Information" })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-2 md:grid-cols-4 gap-4", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(MetaCard, { label: "Sequence Name", value: batch.sequenceName || "Not assigned" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(MetaCard, { label: "Version", value: batch.sequenceVersion || "-" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(MetaCard, { label: "Package", value: batch.sequencePackage || "-" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(MetaCard, { label: "Total Steps", value: (batch.totalSteps ?? 0).toString() })
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-lg p-6 border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mb-4", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-5 h-5 text-brand-500" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: "Step Results" })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(StepsTable, { steps, totalSteps: batch.totalSteps ?? 0, stepNames: batch.stepNames, onStepClick: handleStepRowClick })
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          WipInputModal,
          {
            isOpen: showWipModal,
            onClose: handleWipModalClose,
            onSubmit: handleWipSubmit,
            isLoading: startBatch2.isPending || startSequence2.isPending,
            batchName: batch.name,
            errorMessage: wipError
          }
        )
      ]
    }
  );
}
function MetaCard({ label, value }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-3 rounded-lg", style: { backgroundColor: "var(--color-bg-tertiary)" }, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs mb-1", style: { color: "var(--color-text-tertiary)" }, children: label }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm font-medium truncate", style: { color: "var(--color-text-primary)" }, children: value })
  ] });
}
function StepsTable({ steps, totalSteps, stepNames, onStepClick }) {
  const displaySteps = steps.length > 0 ? steps.map((step, i) => ({
    ...step,
    // Use stepNames as fallback if step.name is generic
    name: step.name.startsWith("Step ") && (stepNames == null ? void 0 : stepNames[i]) ? stepNames[i] : step.name
  })) : Array.from({ length: totalSteps || 0 }, (_, i) => ({
    order: i + 1,
    name: (stepNames == null ? void 0 : stepNames[i]) || `Step ${i + 1}`,
    status: "pending",
    pass: false,
    duration: void 0,
    result: void 0
  }));
  if (displaySteps.length === 0) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: "No steps defined for this sequence" });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "overflow-x-auto", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("table", { className: "w-full text-sm", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("thead", { children: /* @__PURE__ */ jsxRuntimeExports.jsxs("tr", { className: "text-left border-b", style: { color: "var(--color-text-tertiary)", borderColor: "var(--color-border-default)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("th", { className: "pb-3 pr-4 w-12", children: "#" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("th", { className: "pb-3 pr-4", children: "Step Name" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("th", { className: "pb-3 pr-4 w-24", children: "Status" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("th", { className: "pb-3 pr-4 w-20", children: "Result" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("th", { className: "pb-3 pr-4 w-28", children: "Duration" })
    ] }) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("tbody", { children: displaySteps.map((step) => /* @__PURE__ */ jsxRuntimeExports.jsx(StepRow, { step, onClick: onStepClick ? () => onStepClick(step.name) : void 0 }, `${step.order}-${step.name}`)) })
  ] }) });
}
function StepRow({ step, onClick }) {
  const getStatusBadge = () => {
    if (step.status === "completed") return "completed";
    if (step.status === "running") return "running";
    if (step.status === "failed") return "error";
    return "idle";
  };
  const getResultBadge = () => {
    if (step.status === "pending") {
      return /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-zinc-500", children: "-" });
    }
    if (step.status === "running") {
      return /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "flex items-center gap-1 text-brand-500", children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-3 h-3 animate-spin" }) });
    }
    return /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: `font-medium ${step.pass ? "text-green-500" : "text-red-500"}`, children: step.pass ? "PASS" : "FAIL" });
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "tr",
    {
      onClick,
      className: `border-b transition-colors ${onClick ? "cursor-pointer hover:bg-zinc-800/50" : ""}`,
      style: {
        borderColor: "var(--color-border-subtle)",
        backgroundColor: step.status === "running" ? "rgba(var(--color-brand-rgb), 0.1)" : step.status === "failed" ? "rgba(239, 68, 68, 0.1)" : step.pass === false && step.status === "completed" ? "rgba(239, 68, 68, 0.05)" : "transparent"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "py-3 pr-4", style: { color: "var(--color-text-secondary)" }, children: step.order }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "py-3 pr-4 font-medium", style: { color: "var(--color-text-primary)" }, children: step.name }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "py-3 pr-4", children: /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge, { status: getStatusBadge(), size: "sm" }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "py-3 pr-4", children: getResultBadge() }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "py-3 pr-4 font-mono", style: { color: "var(--color-text-secondary)" }, children: step.duration != null ? `${step.duration.toFixed(2)}s` : "-" })
      ]
    }
  );
}
function SequenceUpload({ onSuccess, onClose }) {
  const [isDragOver, setIsDragOver] = reactExports.useState(false);
  const [uploadMode, setUploadMode] = reactExports.useState("zip");
  const [selectedFile, setSelectedFile] = reactExports.useState(null);
  const [selectedFiles, setSelectedFiles] = reactExports.useState(null);
  const [folderName, setFolderName] = reactExports.useState("");
  const [validationResult, setValidationResult] = reactExports.useState(null);
  const [forceOverwrite, setForceOverwrite] = reactExports.useState(false);
  const fileInputRef = reactExports.useRef(null);
  const folderInputRef = reactExports.useRef(null);
  const validateMutation = useValidateSequence();
  const { mutate: uploadZip, progress: zipProgress, isPending: isZipPending, resetProgress: resetZipProgress } = useUploadSequence();
  const { mutate: uploadFolder, progress: folderProgress, isPending: isFolderPending, resetProgress: resetFolderProgress } = useUploadSequenceFolder();
  const progress = uploadMode === "zip" ? zipProgress : folderProgress;
  const isPending = uploadMode === "zip" ? isZipPending : isFolderPending;
  const handleDragOver = reactExports.useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);
  const handleDragLeave = reactExports.useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);
  const handleFileSelect = reactExports.useCallback(
    async (file) => {
      if (!file.name.endsWith(".zip")) {
        setValidationResult({
          valid: false,
          errors: [{ field: "file", message: "Only .zip files are supported" }]
        });
        return;
      }
      setUploadMode("zip");
      setSelectedFile(file);
      setSelectedFiles(null);
      setFolderName("");
      setValidationResult(null);
      resetZipProgress();
      try {
        const result = await validateMutation.mutateAsync(file);
        setValidationResult(result);
      } catch (error) {
        setValidationResult({
          valid: false,
          errors: [
            {
              field: "validation",
              message: error instanceof Error ? error.message : "Validation failed"
            }
          ]
        });
      }
    },
    [validateMutation, resetZipProgress]
  );
  const handleFolderSelect = reactExports.useCallback(
    async (files) => {
      var _a;
      const firstFile = files[0];
      const relativePath = firstFile.webkitRelativePath || "";
      const folderNameFromPath = relativePath.split("/")[0] || "Unknown Folder";
      let hasManifest = false;
      const manifestInfo = {};
      for (let i = 0; i < files.length; i++) {
        const f = files[i];
        if ((_a = f.webkitRelativePath) == null ? void 0 : _a.endsWith("manifest.yaml")) {
          hasManifest = true;
          try {
            const text = await f.text();
            const lines = text.split("\n");
            for (const line of lines) {
              if (line.startsWith("name:")) {
                manifestInfo.name = line.replace("name:", "").trim();
              } else if (line.startsWith("version:")) {
                manifestInfo.version = line.replace("version:", "").trim().replace(/['"]/g, "");
              } else if (line.startsWith("description:")) {
                manifestInfo.description = line.replace("description:", "").trim();
              }
            }
          } catch {
          }
          break;
        }
      }
      setUploadMode("folder");
      setSelectedFile(null);
      setSelectedFiles(files);
      setFolderName(folderNameFromPath);
      resetFolderProgress();
      if (!hasManifest) {
        setValidationResult({
          valid: false,
          errors: [{ field: "folder", message: "manifest.yaml not found in folder" }]
        });
      } else {
        setValidationResult({
          valid: true,
          manifest: manifestInfo.name ? {
            name: manifestInfo.name,
            version: manifestInfo.version || "0.0.0",
            displayName: manifestInfo.name,
            description: manifestInfo.description
          } : void 0
        });
      }
    },
    [resetFolderProgress]
  );
  const handleDrop = reactExports.useCallback(
    async (e) => {
      e.preventDefault();
      setIsDragOver(false);
      const files = e.dataTransfer.files;
      const file = files[0];
      if (file) {
        await handleFileSelect(file);
      }
    },
    [handleFileSelect]
  );
  const handleFileInputChange = reactExports.useCallback(
    async (e) => {
      const files = e.target.files;
      const file = files == null ? void 0 : files[0];
      if (file) {
        await handleFileSelect(file);
      }
    },
    [handleFileSelect]
  );
  const handleFolderInputChange = reactExports.useCallback(
    async (e) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        await handleFolderSelect(files);
      }
    },
    [handleFolderSelect]
  );
  const handleUpload = reactExports.useCallback(() => {
    if (uploadMode === "zip") {
      if (!selectedFile || !(validationResult == null ? void 0 : validationResult.valid)) return;
      uploadZip(
        { file: selectedFile, force: forceOverwrite },
        { onSuccess: () => onSuccess == null ? void 0 : onSuccess() }
      );
    } else {
      if (!selectedFiles || !(validationResult == null ? void 0 : validationResult.valid)) return;
      uploadFolder(
        { files: selectedFiles, force: forceOverwrite },
        { onSuccess: () => onSuccess == null ? void 0 : onSuccess() }
      );
    }
  }, [uploadMode, selectedFile, selectedFiles, validationResult, forceOverwrite, uploadZip, uploadFolder, onSuccess]);
  const handleReset = reactExports.useCallback(() => {
    setSelectedFile(null);
    setSelectedFiles(null);
    setFolderName("");
    setValidationResult(null);
    setForceOverwrite(false);
    resetZipProgress();
    resetFolderProgress();
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    if (folderInputRef.current) {
      folderInputRef.current.value = "";
    }
  }, [resetZipProgress, resetFolderProgress]);
  const handleBrowseZip = reactExports.useCallback(() => {
    var _a;
    (_a = fileInputRef.current) == null ? void 0 : _a.click();
  }, []);
  const handleBrowseFolder = reactExports.useCallback(() => {
    var _a;
    (_a = folderInputRef.current) == null ? void 0 : _a.click();
  }, []);
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-semibold text-white", children: "Upload Sequence Package" }),
      onClose && /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: onClose, children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-4 h-4" }) })
    ] }),
    !selectedFile && !selectedFiles && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          onDragOver: handleDragOver,
          onDragLeave: handleDragLeave,
          onDrop: handleDrop,
          className: `border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer ${isDragOver ? "border-brand-500 bg-brand-500/10" : "border-zinc-600 hover:border-zinc-500"}`,
          onClick: handleBrowseZip,
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "input",
              {
                ref: fileInputRef,
                type: "file",
                accept: ".zip",
                onChange: handleFileInputChange,
                className: "hidden"
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(FileArchive, { className: "w-10 h-10 mx-auto text-zinc-500 mb-3" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-zinc-300 mb-1", children: "Upload ZIP file" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-zinc-500", children: "Drag and drop or click to browse" })
          ]
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex-1 border-t border-zinc-700" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs text-zinc-500", children: "OR" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex-1 border-t border-zinc-700" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer border-zinc-600 hover:border-zinc-500",
          onClick: handleBrowseFolder,
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "input",
              {
                ref: folderInputRef,
                type: "file",
                webkitdirectory: "",
                directory: "",
                multiple: true,
                onChange: handleFolderInputChange,
                className: "hidden"
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(Folder, { className: "w-10 h-10 mx-auto text-zinc-500 mb-3" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-zinc-300 mb-1", children: "Select Folder" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-zinc-500", children: "Choose a sequence package folder" })
          ]
        }
      )
    ] }),
    selectedFile && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "bg-zinc-900/50 rounded-lg p-4 space-y-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(FileArchive, { className: "w-8 h-8 text-brand-500" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 min-w-0", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-medium text-white truncate", children: selectedFile.name }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm text-zinc-500", children: [
            (selectedFile.size / 1024).toFixed(1),
            " KB"
          ] })
        ] }),
        progress.stage === "idle" && /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: handleReset, children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-4 h-4" }) })
      ] }),
      validateMutation.isPending && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 text-zinc-400", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "w-4 h-4 animate-spin" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Validating package..." })
      ] }),
      validationResult && /* @__PURE__ */ jsxRuntimeExports.jsx(
        ValidationStatus,
        {
          result: validationResult,
          onOverwriteChange: setForceOverwrite,
          forceOverwrite
        }
      ),
      progress.stage !== "idle" && /* @__PURE__ */ jsxRuntimeExports.jsx(UploadProgressDisplay, { progress }),
      (validationResult == null ? void 0 : validationResult.valid) && progress.stage === "idle" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 pt-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          Button,
          {
            variant: "primary",
            onClick: handleUpload,
            disabled: isPending,
            className: "flex-1",
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Upload, { className: "w-4 h-4 mr-2" }),
              "Install Package"
            ]
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", onClick: handleReset, children: "Cancel" })
      ] }),
      progress.stage === "complete" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 pt-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "primary", onClick: handleReset, className: "flex-1", children: "Upload Another" }),
        onClose && /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", onClick: onClose, children: "Close" })
      ] }),
      progress.stage === "error" && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex gap-2 pt-2", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "primary", onClick: handleReset, className: "flex-1", children: "Try Again" }) })
    ] }),
    selectedFiles && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "bg-zinc-900/50 rounded-lg p-4 space-y-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Folder, { className: "w-8 h-8 text-brand-500" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 min-w-0", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-medium text-white truncate", children: folderName }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm text-zinc-500", children: [
            selectedFiles.length,
            " files"
          ] })
        ] }),
        progress.stage === "idle" && /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: handleReset, children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-4 h-4" }) })
      ] }),
      validationResult && /* @__PURE__ */ jsxRuntimeExports.jsx(
        ValidationStatus,
        {
          result: validationResult,
          onOverwriteChange: setForceOverwrite,
          forceOverwrite
        }
      ),
      progress.stage !== "idle" && /* @__PURE__ */ jsxRuntimeExports.jsx(UploadProgressDisplay, { progress }),
      (validationResult == null ? void 0 : validationResult.valid) && progress.stage === "idle" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 pt-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          Button,
          {
            variant: "primary",
            onClick: handleUpload,
            disabled: isPending,
            className: "flex-1",
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Upload, { className: "w-4 h-4 mr-2" }),
              "Install Package"
            ]
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", onClick: handleReset, children: "Cancel" })
      ] }),
      progress.stage === "complete" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 pt-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "primary", onClick: handleReset, className: "flex-1", children: "Upload Another" }),
        onClose && /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", onClick: onClose, children: "Close" })
      ] }),
      progress.stage === "error" && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex gap-2 pt-2", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "primary", onClick: handleReset, className: "flex-1", children: "Try Again" }) })
    ] }),
    !selectedFile && !selectedFiles && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "text-xs text-zinc-500 space-y-1", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-medium text-zinc-400", children: "Package Requirements:" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("ul", { className: "list-disc list-inside space-y-0.5", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("li", { children: "Must contain manifest.yaml with name, version, entry_point" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("li", { children: "Must contain the entry_point Python module" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("li", { children: "Optional: drivers/, requirements.txt" })
      ] })
    ] })
  ] });
}
function ValidationStatus({ result, forceOverwrite, onOverwriteChange }) {
  if (result.valid) {
    return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-3", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 text-green-400", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheck, { className: "w-4 h-4" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Package validation passed" })
      ] }),
      result.manifest && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "bg-zinc-800 rounded p-3 space-y-1", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-white font-medium", children: result.manifest.displayName || result.manifest.name }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm text-zinc-400", children: [
          result.manifest.name,
          " v",
          result.manifest.version
        ] }),
        result.manifest.description && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-zinc-500 mt-2", children: result.manifest.description })
      ] }),
      result.warnings && result.warnings.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1", children: [
        result.warnings.map((warning, i) => /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 text-yellow-400 text-sm", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-4 h-4" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: warning })
        ] }, i)),
        result.warnings.some((w) => w.includes("already exists")) && /* @__PURE__ */ jsxRuntimeExports.jsxs("label", { className: "flex items-center gap-2 mt-2 cursor-pointer", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "input",
            {
              type: "checkbox",
              checked: forceOverwrite,
              onChange: (e) => onOverwriteChange(e.target.checked),
              className: "rounded border-zinc-600 bg-zinc-800 text-brand-500 focus:ring-brand-500"
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm text-zinc-300", children: "Overwrite existing package" })
        ] })
      ] })
    ] });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-2", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 text-red-400", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-4 h-4" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Package validation failed" })
    ] }),
    result.errors && result.errors.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "bg-red-900/20 border border-red-800/50 rounded p-3 space-y-1", children: result.errors.map((error, i) => /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm text-red-400", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "font-medium", children: [
        error.field,
        ":"
      ] }),
      " ",
      error.message
    ] }, i)) })
  ] });
}
function UploadProgressDisplay({ progress }) {
  const stageIcon = {
    idle: null,
    validating: /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "w-4 h-4 animate-spin" }),
    uploading: /* @__PURE__ */ jsxRuntimeExports.jsx(Upload, { className: "w-4 h-4" }),
    complete: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheck, { className: "w-4 h-4 text-green-400" }),
    error: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-4 h-4 text-red-400" })
  };
  const stageColor = {
    idle: "text-zinc-400",
    validating: "text-zinc-400",
    uploading: "text-brand-400",
    complete: "text-green-400",
    error: "text-red-400"
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-2", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: `flex items-center gap-2 ${stageColor[progress.stage]}`, children: [
      stageIcon[progress.stage],
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: progress.message })
    ] }),
    (progress.stage === "uploading" || progress.stage === "validating") && /* @__PURE__ */ jsxRuntimeExports.jsx(
      ProgressBar,
      {
        value: progress.progress,
        max: 100,
        variant: "default"
      }
    ),
    progress.error && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-red-400", children: progress.error })
  ] });
}
function SequencesPage() {
  const { sequenceName } = useParams();
  const navigate = useNavigate();
  const [showUpload, setShowUpload] = reactExports.useState(false);
  const { data: sequences, isLoading: listLoading, refetch } = useSequenceList();
  const { data: selectedSequence, isLoading: detailLoading } = useSequence(sequenceName ?? null);
  const deleteMutation = useDeleteSequence();
  const downloadMutation = useDownloadSequence();
  const handleSelectSequence = (name) => {
    navigate(getSequenceDetailRoute(name));
  };
  const handleCloseSequence = () => {
    navigate(ROUTES.SEQUENCES);
  };
  const handleUploadSuccess = () => {
    refetch();
    setShowUpload(false);
  };
  const handleDelete = async (name) => {
    if (!confirm(`Are you sure you want to delete sequence "${name}"?`)) {
      return;
    }
    try {
      await deleteMutation.mutateAsync(name);
      if (sequenceName === name) {
        navigate(ROUTES.SEQUENCES);
      }
    } catch (error) {
      console.error("Failed to delete sequence:", error);
    }
  };
  const handleDownload = async (name) => {
    try {
      await downloadMutation.mutateAsync(name);
    } catch (error) {
      console.error("Failed to download sequence:", error);
    }
  };
  if (listLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingOverlay, { message: "Loading sequences..." });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(GitBranch, { className: "w-6 h-6 text-brand-500" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: "Sequences" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        Button,
        {
          variant: "primary",
          onClick: () => setShowUpload(!showUpload),
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Upload, { className: "w-4 h-4 mr-2" }),
            showUpload ? "Cancel Upload" : "Upload Package"
          ]
        }
      )
    ] }),
    showUpload && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "rounded-lg border p-6", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsx(
      SequenceUpload,
      {
        onSuccess: handleUploadSuccess,
        onClose: () => setShowUpload(false)
      }
    ) }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6 items-start", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("h3", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: [
          "Available Sequences (",
          (sequences == null ? void 0 : sequences.length) ?? 0,
          ")"
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          SequenceList,
          {
            sequences: sequences ?? [],
            selectedName: sequenceName,
            onSelect: handleSelectSequence,
            onDelete: handleDelete,
            onDownload: handleDownload,
            isDeleting: deleteMutation.isPending,
            isDownloading: downloadMutation.isPending
          }
        )
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: "Sequence Details" }),
        sequenceName ? /* @__PURE__ */ jsxRuntimeExports.jsx(
          SequenceDetail,
          {
            sequence: selectedSequence ?? null,
            isLoading: detailLoading,
            onClose: handleCloseSequence,
            onDelete: () => handleDelete(sequenceName),
            onDownload: () => handleDownload(sequenceName)
          }
        ) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "p-8 rounded-lg border text-center", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsx("p", { style: { color: "var(--color-text-tertiary)" }, children: "Select a sequence to view details" }) })
      ] })
    ] })
  ] });
}
function SequenceList({
  sequences,
  selectedName,
  onSelect,
  onDelete,
  onDownload,
  isDeleting,
  isDownloading
}) {
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { children: sequences.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-8 text-center rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)", color: "var(--color-text-tertiary)" }, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { children: "No sequence packages found" }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-2", children: "Upload a package to get started" })
  ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2", children: sequences.map((seq) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "p-4 rounded-lg border transition-colors",
      style: {
        backgroundColor: selectedName === seq.name ? "rgba(var(--color-brand-rgb), 0.1)" : "var(--color-bg-secondary)",
        borderColor: selectedName === seq.name ? "rgba(var(--color-brand-rgb), 0.5)" : "var(--color-border-default)"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "button",
          {
            onClick: () => onSelect(seq.name),
            className: "w-full text-left",
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: seq.displayName }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-1", style: { color: "var(--color-text-tertiary)" }, children: seq.name })
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-xs px-2 py-1 rounded", style: { backgroundColor: "var(--color-bg-tertiary)", color: "var(--color-text-secondary)" }, children: [
                    "v",
                    seq.version
                  ] }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronRight, { className: "w-4 h-4", style: { color: "var(--color-text-secondary)" } })
                ] })
              ] }),
              seq.description && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-2 line-clamp-2", style: { color: "var(--color-text-secondary)" }, children: seq.description })
            ]
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 mt-3 pt-3 border-t", style: { borderColor: "var(--color-border-subtle)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "button",
            {
              onClick: (e) => {
                e.stopPropagation();
                onDownload(seq.name);
              },
              disabled: isDownloading,
              className: "flex items-center gap-1 px-2 py-1 text-xs rounded transition-colors disabled:opacity-50",
              style: { color: "var(--color-text-secondary)" },
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Download, { className: "w-3 h-3" }),
                "Download"
              ]
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "button",
            {
              onClick: (e) => {
                e.stopPropagation();
                onDelete(seq.name);
              },
              disabled: isDeleting,
              className: "flex items-center gap-1 px-2 py-1 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition-colors disabled:opacity-50",
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Trash2, { className: "w-3 h-3" }),
                "Delete"
              ]
            }
          )
        ] })
      ]
    },
    seq.name
  )) }) });
}
function SequenceDetail({ sequence, isLoading, onClose, onDelete, onDownload }) {
  const [activeTab, setActiveTab] = reactExports.useState("steps");
  if (isLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "p-8 flex items-center justify-center rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "lg" }) });
  }
  if (!sequence) {
    return null;
  }
  const defaultParameters = sequence.parameters.reduce(
    (acc, p) => ({ ...acc, [p.name]: p.default }),
    {}
  );
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 border-b", style: { borderColor: "var(--color-border-default)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: sequence.displayName }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: [
            sequence.name,
            " v",
            sequence.version
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: onDownload, children: /* @__PURE__ */ jsxRuntimeExports.jsx(Download, { className: "w-4 h-4" }) }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: onDelete, className: "text-red-400 hover:text-red-300", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Trash2, { className: "w-4 h-4" }) }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: onClose, children: "Close" })
        ] })
      ] }),
      sequence.description && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-2", style: { color: "var(--color-text-secondary)" }, children: sequence.description }),
      sequence.author && /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs mt-1", style: { color: "var(--color-text-tertiary)" }, children: [
        "Author: ",
        sequence.author
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex border-b", style: { borderColor: "var(--color-border-default)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        TabButton,
        {
          active: activeTab === "steps",
          onClick: () => setActiveTab("steps"),
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(ArrowRight, { className: "w-4 h-4" }),
          label: `Steps (${sequence.steps.length})`
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        TabButton,
        {
          active: activeTab === "params",
          onClick: () => setActiveTab("params"),
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Settings2, { className: "w-4 h-4" }),
          label: `Parameters (${sequence.parameters.length})`
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        TabButton,
        {
          active: activeTab === "hardware",
          onClick: () => setActiveTab("hardware"),
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Cpu, { className: "w-4 h-4" }),
          label: `Hardware (${sequence.hardware.length})`
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        TabButton,
        {
          active: activeTab === "test",
          onClick: () => setActiveTab("test"),
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Zap, { className: "w-4 h-4" }),
          label: "Test"
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 max-h-[500px] overflow-y-auto", children: [
      activeTab === "steps" && /* @__PURE__ */ jsxRuntimeExports.jsx(StepList, { steps: sequence.steps }),
      activeTab === "params" && /* @__PURE__ */ jsxRuntimeExports.jsx(ParameterList, { parameters: sequence.parameters }),
      activeTab === "hardware" && /* @__PURE__ */ jsxRuntimeExports.jsx(HardwareList, { hardware: sequence.hardware }),
      activeTab === "test" && /* @__PURE__ */ jsxRuntimeExports.jsx(
        TestTabContent,
        {
          sequenceName: sequence.name,
          defaultParameters
        }
      )
    ] })
  ] });
}
function TabButton({ active, onClick, icon, label }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "button",
    {
      onClick,
      className: "flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors",
      style: {
        color: active ? "var(--color-brand-500)" : "var(--color-text-secondary)",
        borderBottom: active ? "2px solid var(--color-brand-500)" : "none"
      },
      children: [
        icon,
        label
      ]
    }
  );
}
function StepList({ steps }) {
  if (steps.length === 0) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: "No steps defined" });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2", children: steps.map((step) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "flex items-center gap-3 p-3 rounded-lg",
      style: { backgroundColor: "var(--color-bg-tertiary)" },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "w-6 h-6 flex items-center justify-center text-xs font-medium rounded-full", style: { backgroundColor: "var(--color-bg-secondary)", color: "var(--color-text-secondary)" }, children: step.order }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: step.displayName }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: step.name })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 text-xs", style: { color: "var(--color-text-secondary)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-3 h-3" }),
          step.timeout,
          "s"
        ] }),
        step.cleanup && /* @__PURE__ */ jsxRuntimeExports.jsx(
          "span",
          {
            className: "text-xs px-2 py-0.5 rounded",
            style: { backgroundColor: "var(--color-warning-bg)", color: "var(--color-warning-text)" },
            children: "cleanup"
          }
        )
      ]
    },
    step.name
  )) });
}
function ParameterList({ parameters }) {
  if (parameters.length === 0) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: "No parameters defined" });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2", children: parameters.map((param) => /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-3 rounded-lg", style: { backgroundColor: "var(--color-bg-tertiary)" }, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: param.displayName }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: param.name })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs px-2 py-0.5 rounded", style: { backgroundColor: "var(--color-bg-secondary)", color: "var(--color-text-secondary)" }, children: param.type })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-2 flex items-center gap-4 text-xs", style: { color: "var(--color-text-secondary)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
        "Default: ",
        String(param.default ?? "none")
      ] }),
      param.min !== void 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
        "Min: ",
        param.min
      ] }),
      param.max !== void 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
        "Max: ",
        param.max
      ] }),
      param.unit && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
        "Unit: ",
        param.unit
      ] })
    ] })
  ] }, param.name)) });
}
function HardwareList({ hardware }) {
  if (hardware.length === 0) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: "No hardware defined" });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2", children: hardware.map((hw) => /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-3 rounded-lg", style: { backgroundColor: "var(--color-bg-tertiary)" }, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: hw.displayName }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: hw.id })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(Cpu, { className: "w-4 h-4", style: { color: "var(--color-text-secondary)" } })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-2 text-xs", style: { color: "var(--color-text-secondary)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
        "Driver: ",
        hw.driver
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "ml-4", children: [
        "Class: ",
        hw.className
      ] })
    ] })
  ] }, hw.id)) });
}
function TestTabContent({ sequenceName, defaultParameters }) {
  const [mode, setMode] = reactExports.useState("preview");
  const [expanded, setExpanded] = reactExports.useState(false);
  const [result, setResult] = reactExports.useState(null);
  const simulation = useSimulation();
  const handleRun = async () => {
    try {
      const simResult = await simulation.mutateAsync({
        sequenceName,
        mode,
        parameters: defaultParameters
      });
      setResult(simResult);
      setExpanded(true);
    } catch (error) {
      console.error("Simulation failed:", error);
    }
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "button",
        {
          onClick: () => setMode("preview"),
          className: "flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border transition-colors",
          style: {
            borderColor: mode === "preview" ? "var(--color-brand-500)" : "var(--color-border-default)",
            backgroundColor: mode === "preview" ? "rgba(var(--color-brand-rgb), 0.1)" : "var(--color-bg-tertiary)",
            color: mode === "preview" ? "var(--color-brand-500)" : "var(--color-text-secondary)"
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Eye, { className: "w-4 h-4" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", children: "Preview" })
          ]
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "button",
        {
          onClick: () => setMode("dry_run"),
          className: "flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border transition-colors",
          style: {
            borderColor: mode === "dry_run" ? "var(--color-brand-500)" : "var(--color-border-default)",
            backgroundColor: mode === "dry_run" ? "rgba(var(--color-brand-rgb), 0.1)" : "var(--color-bg-tertiary)",
            color: mode === "dry_run" ? "var(--color-brand-500)" : "var(--color-text-secondary)"
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-4 h-4" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", children: "Dry Run" })
          ]
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-zinc-500", children: mode === "preview" ? "View step information without executing any code." : "Execute sequence with mock hardware for testing." }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      Button,
      {
        variant: "primary",
        className: "w-full",
        onClick: handleRun,
        isLoading: simulation.isPending,
        disabled: simulation.isPending,
        children: simulation.isPending ? "Running..." : /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-4 h-4 mr-2" }),
          "Run ",
          mode === "preview" ? "Preview" : "Dry Run"
        ] })
      }
    ),
    simulation.isError && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-3 bg-red-500/10 border border-red-500/30 rounded-lg", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 text-red-400", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-4 h-4" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", children: "Simulation Failed" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-red-300/80 mt-1", children: simulation.error.message || "Unknown error" })
    ] }),
    result && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "border rounded-lg overflow-hidden", style: { borderColor: "var(--color-border-default)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "button",
        {
          onClick: () => setExpanded(!expanded),
          className: "w-full p-3 flex items-center justify-between transition-colors",
          style: { backgroundColor: "var(--color-bg-tertiary)" },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
              result.status === "completed" ? /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-4 h-4 text-green-500" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-4 h-4 text-red-500" }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: [
                result.mode === "preview" ? "Preview" : "Dry Run",
                " - ",
                result.status
              ] })
            ] }),
            expanded ? /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronUp, { className: "w-4 h-4", style: { color: "var(--color-text-secondary)" } }) : /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronDown, { className: "w-4 h-4", style: { color: "var(--color-text-secondary)" } })
          ]
        }
      ),
      expanded && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-3 space-y-3 max-h-64 overflow-y-auto", children: [
        result.steps.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-2", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "text-xs font-medium uppercase", style: { color: "var(--color-text-secondary)" }, children: "Steps" }),
          result.steps.map((step) => {
            var _a;
            return /* @__PURE__ */ jsxRuntimeExports.jsx(
              StepPreviewItem,
              {
                step,
                result: (_a = result.stepResults) == null ? void 0 : _a.find(
                  (r) => r.name === step.name
                )
              },
              step.name
            );
          })
        ] }),
        result.error && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-2 bg-red-500/10 rounded text-xs text-red-400", children: [
          "Error: ",
          result.error
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-4 text-xs pt-2 border-t", style: { color: "var(--color-text-tertiary)", borderColor: "var(--color-border-default)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
            "ID: ",
            result.id
          ] }),
          result.completedAt && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex items-center gap-1", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-3 h-3" }),
            new Date(result.completedAt).toLocaleTimeString()
          ] })
        ] })
      ] })
    ] })
  ] });
}
function StepPreviewItem({ step, result }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3 p-2 rounded", style: { backgroundColor: "var(--color-bg-tertiary)" }, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      "span",
      {
        className: "w-5 h-5 flex items-center justify-center text-xs font-medium rounded-full",
        style: {
          backgroundColor: (result == null ? void 0 : result.status) === "passed" ? "rgba(34, 197, 94, 0.2)" : (result == null ? void 0 : result.status) === "failed" ? "rgba(239, 68, 68, 0.2)" : "var(--color-bg-secondary)",
          color: (result == null ? void 0 : result.status) === "passed" ? "#4ade80" : (result == null ? void 0 : result.status) === "failed" ? "#f87171" : "var(--color-text-secondary)"
        },
        children: step.order
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 min-w-0", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium truncate", style: { color: "var(--color-text-primary)" }, children: step.displayName }),
        step.cleanup && /* @__PURE__ */ jsxRuntimeExports.jsx(
          "span",
          {
            className: "text-xs px-1.5 py-0.5 rounded",
            style: { backgroundColor: "var(--color-warning-bg)", color: "var(--color-warning-text)" },
            children: "cleanup"
          }
        )
      ] }),
      step.description && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs truncate", style: { color: "var(--color-text-tertiary)" }, children: step.description })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1 text-xs", style: { color: "var(--color-text-secondary)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-3 h-3" }),
      result ? /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: result.status === "passed" ? "text-green-400" : "text-red-400", children: [
        result.duration.toFixed(1),
        "s"
      ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
        step.timeout,
        "s"
      ] })
    ] }),
    result && (result.status === "passed" ? /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-4 h-4 text-green-500" }) : result.status === "failed" ? /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-4 h-4 text-red-500" }) : null)
  ] });
}
function isBatchDetail(data) {
  return data !== null && typeof data === "object" && "hardwareStatus" in data;
}
const CATEGORY_ICONS = {
  measurement: Gauge,
  control: Zap,
  configuration: Settings,
  diagnostic: Search
};
const CATEGORY_LABELS = {
  measurement: "Measurement",
  control: "Control",
  configuration: "Configuration",
  diagnostic: "Diagnostic"
};
function ManualControlPage() {
  const { data: batches2, isLoading } = useBatchList();
  const [activeTab, setActiveTab] = reactExports.useState("commands");
  const selectedBatchId = useManualControlStore((s) => s.selectedBatchId);
  const selectedHardwareId = useManualControlStore((s) => s.selectedHardwareId);
  const selectDevice = useManualControlStore((s) => s.selectDevice);
  const selectedCommand = useManualControlStore((s) => s.selectedCommand);
  const selectCommand = useManualControlStore((s) => s.selectCommand);
  const parameterValues = useManualControlStore((s) => s.parameterValues);
  const setParameterValue = useManualControlStore((s) => s.setParameterValue);
  const resultHistory = useManualControlStore((s) => s.resultHistory);
  const { data: batchDetail } = useBatch(selectedBatchId);
  const { data: commandsData, isLoading: loadingCommands } = useHardwareCommands(
    selectedBatchId,
    selectedHardwareId
  );
  const executeCommand = useExecuteCommand();
  const groupedCommands = reactExports.useMemo(() => {
    if (!(commandsData == null ? void 0 : commandsData.commands)) return {};
    return selectGroupedCommands(commandsData.commands);
  }, [commandsData]);
  const batchOptions = reactExports.useMemo(() => {
    return (batches2 == null ? void 0 : batches2.filter((b) => b.status === "idle").map((b) => ({
      value: b.id,
      label: `${b.name} - ${b.sequenceName ?? "No sequence"}`
    }))) ?? [];
  }, [batches2]);
  const hardwareOptions = reactExports.useMemo(() => {
    if (!isBatchDetail(batchDetail) || !batchDetail.hardwareStatus) return [];
    return Object.entries(batchDetail.hardwareStatus).map(([id, status]) => ({
      value: id,
      label: `${id} (${status.driver})`
    }));
  }, [batchDetail]);
  const handleExecute = async () => {
    if (!selectedBatchId || !selectedHardwareId || !selectedCommand) return;
    await executeCommand.mutateAsync({
      batchId: selectedBatchId,
      request: {
        hardware: selectedHardwareId,
        command: selectedCommand.name,
        params: parameterValues
      },
      command: selectedCommand
    });
  };
  if (isLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingOverlay, { message: "Loading batches..." });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Wrench, { className: "w-6 h-6 text-brand-500" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "h2",
          {
            className: "text-2xl font-bold",
            style: { color: "var(--color-text-primary)" },
            children: "Manual Control"
          }
        )
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 p-1 rounded-lg", style: { backgroundColor: "var(--color-bg-tertiary)" }, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "button",
          {
            onClick: () => setActiveTab("commands"),
            className: cn(
              "px-4 py-2 rounded-md text-sm font-medium transition-all",
              activeTab === "commands" ? "bg-brand-500 text-white" : "hover:bg-brand-500/20"
            ),
            style: activeTab !== "commands" ? { color: "var(--color-text-secondary)" } : {},
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Cpu, { className: "w-4 h-4 inline mr-2" }),
              "Hardware Commands"
            ]
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "button",
          {
            onClick: () => setActiveTab("sequence"),
            className: cn(
              "px-4 py-2 rounded-md text-sm font-medium transition-all",
              activeTab === "sequence" ? "bg-brand-500 text-white" : "hover:bg-brand-500/20"
            ),
            style: activeTab !== "sequence" ? { color: "var(--color-text-secondary)" } : {},
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(ListOrdered, { className: "w-4 h-4 inline mr-2" }),
              "Manual Sequence"
            ]
          }
        )
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-5 h-5 text-yellow-500 flex-shrink-0" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-yellow-400 text-sm", children: "Manual control mode. Use with caution - direct hardware access can affect system state." })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "p-4 rounded-lg border flex flex-wrap gap-4 items-end",
        style: {
          backgroundColor: "var(--color-bg-secondary)",
          borderColor: "var(--color-border-default)"
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex-1 min-w-[200px]", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
            Select,
            {
              label: "Test Station (Batch)",
              options: batchOptions,
              value: selectedBatchId ?? "",
              onChange: (e) => {
                selectDevice(e.target.value || null, null);
                selectCommand(null);
              },
              placeholder: "Select idle batch..."
            }
          ) }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex-1 min-w-[200px]", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
            Select,
            {
              label: "Hardware Device",
              options: hardwareOptions,
              value: selectedHardwareId ?? "",
              onChange: (e) => {
                selectDevice(selectedBatchId, e.target.value || null);
                selectCommand(null);
              },
              placeholder: "Select hardware...",
              disabled: !selectedBatchId
            }
          ) }),
          commandsData && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              StatusBadge,
              {
                status: commandsData.connected ? "connected" : "disconnected",
                size: "sm"
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: commandsData.driver })
          ] })
        ]
      }
    ),
    activeTab === "commands" ? /* @__PURE__ */ jsxRuntimeExports.jsx(
      CommandsTab,
      {
        groupedCommands,
        selectedCommand,
        selectCommand,
        parameterValues,
        setParameterValue,
        resultHistory,
        onExecute: handleExecute,
        isExecuting: executeCommand.isPending,
        isDisabled: !selectedBatchId || !selectedHardwareId,
        loadingCommands
      }
    ) : /* @__PURE__ */ jsxRuntimeExports.jsx(SequenceTab, { batchId: selectedBatchId })
  ] });
}
function CommandsTab({
  groupedCommands,
  selectedCommand,
  selectCommand,
  parameterValues,
  setParameterValue,
  resultHistory,
  onExecute,
  isExecuting,
  isDisabled,
  loadingCommands
}) {
  var _a, _b;
  const [activeCategory, setActiveCategory] = reactExports.useState("measurement");
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "p-4 rounded-lg border space-y-4",
        style: {
          backgroundColor: "var(--color-bg-secondary)",
          borderColor: "var(--color-border-default)"
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "h3",
            {
              className: "text-lg font-semibold",
              style: { color: "var(--color-text-primary)" },
              children: "Commands"
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex flex-wrap gap-1", children: Object.entries(CATEGORY_LABELS).map(([key, label]) => {
            var _a2;
            const Icon2 = CATEGORY_ICONS[key];
            const count = ((_a2 = groupedCommands[key]) == null ? void 0 : _a2.length) ?? 0;
            return /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "button",
              {
                onClick: () => setActiveCategory(key),
                className: cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all",
                  activeCategory === key ? "bg-brand-500 text-white" : "hover:bg-brand-500/20"
                ),
                style: activeCategory !== key ? { color: "var(--color-text-secondary)" } : {},
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Icon2, { className: "w-3.5 h-3.5" }),
                  label,
                  count > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx(
                    "span",
                    {
                      className: cn(
                        "px-1.5 py-0.5 rounded text-xs",
                        activeCategory === key ? "bg-white/20" : "bg-gray-600/50"
                      ),
                      children: count
                    }
                  )
                ]
              },
              key
            );
          }) }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-1 max-h-64 overflow-y-auto", children: loadingCommands ? /* @__PURE__ */ jsxRuntimeExports.jsx(
            "p",
            {
              className: "text-sm py-4 text-center",
              style: { color: "var(--color-text-tertiary)" },
              children: "Loading commands..."
            }
          ) : (((_a = groupedCommands[activeCategory]) == null ? void 0 : _a.length) ?? 0) === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx(
            "p",
            {
              className: "text-sm py-4 text-center",
              style: { color: "var(--color-text-tertiary)" },
              children: isDisabled ? "Select a batch and hardware device" : "No commands available"
            }
          ) : (_b = groupedCommands[activeCategory]) == null ? void 0 : _b.map((cmd) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "button",
            {
              onClick: () => selectCommand(cmd),
              className: cn(
                "w-full text-left px-3 py-2 rounded-md transition-all",
                (selectedCommand == null ? void 0 : selectedCommand.name) === cmd.name ? "bg-brand-500/20 border border-brand-500/50" : "hover:bg-brand-500/10"
              ),
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "div",
                  {
                    className: "font-medium text-sm",
                    style: { color: "var(--color-text-primary)" },
                    children: cmd.displayName
                  }
                ),
                cmd.description && /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "div",
                  {
                    className: "text-xs mt-0.5 line-clamp-1",
                    style: { color: "var(--color-text-tertiary)" },
                    children: cmd.description
                  }
                )
              ]
            },
            cmd.name
          )) })
        ]
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "p-4 rounded-lg border space-y-4",
        style: {
          backgroundColor: "var(--color-bg-secondary)",
          borderColor: "var(--color-border-default)"
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "h3",
            {
              className: "text-lg font-semibold",
              style: { color: "var(--color-text-primary)" },
              children: (selectedCommand == null ? void 0 : selectedCommand.displayName) ?? "Parameters"
            }
          ),
          selectedCommand ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
            selectedCommand.description && /* @__PURE__ */ jsxRuntimeExports.jsx(
              "p",
              {
                className: "text-sm",
                style: { color: "var(--color-text-tertiary)" },
                children: selectedCommand.description
              }
            ),
            selectedCommand.parameters.length > 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-3", children: selectedCommand.parameters.map((param) => /* @__PURE__ */ jsxRuntimeExports.jsx(
              ParameterInput,
              {
                parameter: param,
                value: parameterValues[param.name],
                onChange: (v) => setParameterValue(param.name, v)
              },
              param.name
            )) }) : /* @__PURE__ */ jsxRuntimeExports.jsx(
              "p",
              {
                className: "text-sm italic",
                style: { color: "var(--color-text-tertiary)" },
                children: "No parameters required"
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              Button,
              {
                variant: "primary",
                className: "w-full mt-4",
                onClick: onExecute,
                isLoading: isExecuting,
                disabled: isDisabled,
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Send, { className: "w-4 h-4 mr-2" }),
                  "Execute ",
                  selectedCommand.displayName
                ]
              }
            ),
            selectedCommand.returnUnit && /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "p",
              {
                className: "text-xs text-center",
                style: { color: "var(--color-text-tertiary)" },
                children: [
                  "Returns: ",
                  selectedCommand.returnType,
                  " (",
                  selectedCommand.returnUnit,
                  ")"
                ]
              }
            )
          ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx(
            "p",
            {
              className: "text-sm py-8 text-center",
              style: { color: "var(--color-text-tertiary)" },
              children: "Select a command to configure parameters"
            }
          )
        ]
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "p-4 rounded-lg border space-y-4",
        style: {
          backgroundColor: "var(--color-bg-secondary)",
          borderColor: "var(--color-border-default)"
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "h3",
            {
              className: "text-lg font-semibold flex items-center gap-2",
              style: { color: "var(--color-text-primary)" },
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(History, { className: "w-5 h-5" }),
                "Results"
              ]
            }
          ),
          resultHistory[0] && /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "div",
            {
              className: cn(
                "p-3 rounded-lg border",
                resultHistory[0].success ? "border-green-500/30 bg-green-500/10" : "border-red-500/30 bg-red-500/10"
              ),
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-2", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsxs(
                    "span",
                    {
                      className: "text-sm font-medium",
                      style: { color: "var(--color-text-secondary)" },
                      children: [
                        resultHistory[0].hardware,
                        ".",
                        resultHistory[0].command
                      ]
                    }
                  ),
                  /* @__PURE__ */ jsxRuntimeExports.jsx(
                    StatusBadge,
                    {
                      status: resultHistory[0].success ? "pass" : "fail",
                      size: "sm"
                    }
                  )
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  "div",
                  {
                    className: "text-2xl font-bold",
                    style: { color: "var(--color-text-primary)" },
                    children: [
                      formatResult(resultHistory[0].result),
                      resultHistory[0].unit && /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm ml-1", children: resultHistory[0].unit })
                    ]
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  "div",
                  {
                    className: "text-xs mt-1",
                    style: { color: "var(--color-text-tertiary)" },
                    children: [
                      resultHistory[0].duration,
                      "ms"
                    ]
                  }
                )
              ]
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-1 max-h-64 overflow-y-auto", children: resultHistory.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx(
            "p",
            {
              className: "text-sm text-center py-4",
              style: { color: "var(--color-text-tertiary)" },
              children: "No commands executed yet"
            }
          ) : resultHistory.slice(1).map((entry) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "div",
            {
              className: "flex items-center justify-between p-2 rounded-md text-sm",
              style: { backgroundColor: "var(--color-bg-tertiary)" },
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
                  entry.success ? /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-4 h-4 text-green-500" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-4 h-4 text-red-500" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: entry.command })
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "span",
                  {
                    className: "text-xs",
                    style: { color: "var(--color-text-tertiary)" },
                    children: entry.timestamp.toLocaleTimeString()
                  }
                )
              ]
            },
            entry.id
          )) })
        ]
      }
    )
  ] });
}
function SequenceTab({ batchId }) {
  const { data: steps, isLoading } = useManualSteps(batchId);
  const sequenceSteps = useManualControlStore((s) => s.sequenceSteps);
  const currentStepIndex = useManualControlStore((s) => s.currentStepIndex);
  const stepOverrides = useManualControlStore((s) => s.stepOverrides);
  const setStepOverride = useManualControlStore((s) => s.setStepOverride);
  const runStep = useRunManualStep();
  const skipStep = useSkipManualStep();
  const resetSequence = useResetManualSequence();
  const handleRunStep = (stepName) => {
    if (!batchId) return;
    runStep.mutate({
      batchId,
      stepName,
      parameters: stepOverrides[stepName]
    });
  };
  const handleSkipStep = (stepName) => {
    if (!batchId) return;
    skipStep.mutate({ batchId, stepName });
  };
  const handleReset = () => {
    if (!batchId) return;
    resetSequence.mutate(batchId);
  };
  if (!batchId) {
    return /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "p-8 text-center rounded-lg border",
        style: {
          backgroundColor: "var(--color-bg-secondary)",
          borderColor: "var(--color-border-default)"
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            ListOrdered,
            {
              className: "w-12 h-12 mx-auto mb-4",
              style: { color: "var(--color-text-tertiary)" }
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { style: { color: "var(--color-text-tertiary)" }, children: "Select a batch to view sequence steps" })
        ]
      }
    );
  }
  if (isLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingOverlay, { message: "Loading sequence steps..." });
  }
  const displaySteps = sequenceSteps.length > 0 ? sequenceSteps : steps ?? [];
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "p-4 rounded-lg border",
      style: {
        backgroundColor: "var(--color-bg-secondary)",
        borderColor: "var(--color-border-default)"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "h3",
            {
              className: "text-lg font-semibold flex items-center gap-2",
              style: { color: "var(--color-text-primary)" },
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(ListOrdered, { className: "w-5 h-5" }),
                "Manual Sequence Execution"
              ]
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "ghost", size: "sm", onClick: handleReset, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(RotateCcw, { className: "w-4 h-4 mr-1" }),
            "Reset"
          ] })
        ] }),
        displaySteps.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx(
          "p",
          {
            className: "text-sm text-center py-8",
            style: { color: "var(--color-text-tertiary)" },
            children: "No sequence steps available"
          }
        ) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2", children: displaySteps.map((step, index) => /* @__PURE__ */ jsxRuntimeExports.jsx(
          StepCard,
          {
            step,
            index,
            isCurrent: index === currentStepIndex,
            overrides: stepOverrides[step.name],
            onRun: () => handleRunStep(step.name),
            onSkip: () => handleSkipStep(step.name),
            onUpdateOverrides: (overrides) => setStepOverride(step.name, overrides),
            isRunning: runStep.isPending
          },
          step.name
        )) }),
        displaySteps.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 mt-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs(
            Button,
            {
              className: "flex-1",
              onClick: () => {
                const nextPending = displaySteps.find(
                  (s) => s.status === "pending"
                );
                if (nextPending) {
                  handleRunStep(nextPending.name);
                }
              },
              disabled: !displaySteps.some((s) => s.status === "pending") || runStep.isPending,
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-4 h-4 mr-1" }),
                "Run Next Step"
              ]
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsxs(
            Button,
            {
              variant: "secondary",
              disabled: true,
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(FastForward, { className: "w-4 h-4 mr-1" }),
                "Run All Remaining"
              ]
            }
          )
        ] })
      ]
    }
  );
}
function StepCard({
  step,
  index,
  isCurrent,
  overrides: _overrides,
  onRun,
  onSkip,
  onUpdateOverrides: _onUpdateOverrides,
  isRunning
}) {
  var _a, _b;
  const [isExpanded, setIsExpanded] = reactExports.useState(false);
  const statusColors = {
    pending: "border-gray-500/30",
    running: "border-blue-500 bg-blue-500/10",
    completed: "border-green-500 bg-green-500/10",
    failed: "border-red-500 bg-red-500/10",
    skipped: "border-gray-500 bg-gray-500/10"
  };
  const StatusIcon = {
    pending: Clock,
    running: Play,
    completed: CircleCheckBig,
    failed: CircleX,
    skipped: SkipForward
  }[step.status];
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: cn(
        "p-3 rounded-lg border transition-all",
        statusColors[step.status],
        isCurrent && "ring-2 ring-brand-500"
      ),
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              StatusIcon,
              {
                className: cn(
                  "w-5 h-5",
                  step.status === "running" && "animate-pulse",
                  step.status === "completed" && "text-green-500",
                  step.status === "failed" && "text-red-500",
                  step.status === "skipped" && "text-gray-500"
                ),
                style: step.status === "pending" || step.status === "running" ? { color: "var(--color-text-secondary)" } : {}
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "span",
                {
                  className: "font-medium",
                  style: { color: "var(--color-text-primary)" },
                  children: [
                    index + 1,
                    ". ",
                    step.displayName
                  ]
                }
              ),
              step.duration !== void 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "span",
                {
                  className: "ml-2 text-xs",
                  style: { color: "var(--color-text-tertiary)" },
                  children: [
                    step.duration.toFixed(1),
                    "s"
                  ]
                }
              )
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
            step.status === "pending" && isCurrent && /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { size: "sm", onClick: onRun, isLoading: isRunning, children: /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-3 h-3" }) }),
              ((_a = step.manual) == null ? void 0 : _a.skippable) && /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { size: "sm", variant: "ghost", onClick: onSkip, children: "Skip" })
            ] }),
            step.status === "failed" && /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { size: "sm", variant: "secondary", onClick: onRun, children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(RotateCcw, { className: "w-3 h-3 mr-1" }),
              "Retry"
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Button,
              {
                size: "sm",
                variant: "ghost",
                onClick: () => setIsExpanded(!isExpanded),
                children: isExpanded ? /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronUp, {}) : /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronDown, {})
              }
            )
          ] })
        ] }),
        isExpanded && /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "mt-3 pt-3 border-t",
            style: { borderColor: "var(--color-border-default)" },
            children: [
              ((_b = step.manual) == null ? void 0 : _b.prompt) && /* @__PURE__ */ jsxRuntimeExports.jsx(
                "p",
                {
                  className: "text-sm mb-2 italic",
                  style: { color: "var(--color-text-tertiary)" },
                  children: step.manual.prompt
                }
              ),
              step.result && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-2", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "h4",
                  {
                    className: "text-sm font-medium mb-1",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Result"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "pre",
                  {
                    className: "text-xs p-2 rounded overflow-auto max-h-32",
                    style: {
                      backgroundColor: "var(--color-bg-tertiary)",
                      color: "var(--color-text-secondary)"
                    },
                    children: JSON.stringify(step.result, null, 2)
                  }
                )
              ] })
            ]
          }
        )
      ]
    }
  );
}
function ParameterInput({ parameter, value, onChange }) {
  var _a;
  switch (parameter.type) {
    case "number":
      return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "label",
          {
            className: "block text-sm font-medium mb-1",
            style: { color: "var(--color-text-secondary)" },
            children: [
              parameter.displayName,
              parameter.unit && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "ml-1 text-xs", children: [
                "(",
                parameter.unit,
                ")"
              ] })
            ]
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "input",
          {
            type: "number",
            value: value ?? parameter.default ?? "",
            onChange: (e) => onChange(parseFloat(e.target.value) || 0),
            min: parameter.min,
            max: parameter.max,
            step: "any",
            className: "w-full px-3 py-2 rounded-lg text-sm",
            style: {
              backgroundColor: "var(--color-bg-tertiary)",
              borderColor: "var(--color-border-default)",
              color: "var(--color-text-primary)"
            }
          }
        ),
        (parameter.min !== void 0 || parameter.max !== void 0) && /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "p",
          {
            className: "text-xs mt-1",
            style: { color: "var(--color-text-tertiary)" },
            children: [
              "Range: ",
              parameter.min ?? "-∞",
              " to ",
              parameter.max ?? "∞"
            ]
          }
        )
      ] });
    case "boolean":
      return /* @__PURE__ */ jsxRuntimeExports.jsxs("label", { className: "flex items-center gap-2 cursor-pointer", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "input",
          {
            type: "checkbox",
            checked: value ?? parameter.default ?? false,
            onChange: (e) => onChange(e.target.checked),
            className: "w-4 h-4 rounded"
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: parameter.displayName })
      ] });
    case "select":
      return /* @__PURE__ */ jsxRuntimeExports.jsx(
        Select,
        {
          label: parameter.displayName,
          value: String(value ?? parameter.default ?? ""),
          onChange: (e) => onChange(e.target.value),
          options: ((_a = parameter.options) == null ? void 0 : _a.map((opt) => ({
            value: String(opt.value),
            label: opt.label
          }))) ?? []
        }
      );
    default:
      return /* @__PURE__ */ jsxRuntimeExports.jsx(
        Input,
        {
          label: parameter.displayName,
          value: String(value ?? parameter.default ?? ""),
          onChange: (e) => onChange(e.target.value),
          placeholder: parameter.description
        }
      );
  }
}
function formatResult(result) {
  if (typeof result === "number") {
    return result.toFixed(4);
  }
  if (typeof result === "boolean") {
    return result ? "TRUE" : "FALSE";
  }
  if (typeof result === "string") {
    return result;
  }
  if (result === null || result === void 0) {
    return "-";
  }
  return JSON.stringify(result);
}
function LogsPage() {
  const { data: batches2 } = useBatchList();
  const [batchFilter, setBatchFilter] = reactExports.useState("");
  const [levelFilter, setLevelFilter] = reactExports.useState("");
  const [searchFilter, setSearchFilter] = reactExports.useState("");
  const [showHistorical, setShowHistorical] = reactExports.useState(false);
  const realTimeLogs = useLogStore((state) => state.logs);
  const autoScroll = useLogStore((state) => state.autoScroll);
  const setAutoScroll = useLogStore((state) => state.setAutoScroll);
  const clearLogs = useLogStore((state) => state.clearLogs);
  const setFilters = useLogStore((state) => state.setFilters);
  const { data: historicalLogs, isLoading: historicalLoading } = useLogList(
    showHistorical ? {
      batchId: batchFilter || void 0,
      level: levelFilter || void 0,
      search: searchFilter || void 0,
      limit: 100
    } : void 0
  );
  const logContainerRef = reactExports.useRef(null);
  reactExports.useEffect(() => {
    setFilters({
      batchId: batchFilter || void 0,
      level: levelFilter || void 0,
      search: searchFilter || void 0
    });
  }, [batchFilter, levelFilter, searchFilter, setFilters]);
  reactExports.useEffect(() => {
    if (autoScroll && logContainerRef.current && !showHistorical) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [realTimeLogs, autoScroll, showHistorical]);
  const batchOptions = [
    { value: "", label: "All Batches" },
    ...(batches2 == null ? void 0 : batches2.map((b) => ({ value: b.id, label: b.name }))) ?? []
  ];
  const levelOptions2 = [
    { value: "", label: "All Levels" },
    { value: "debug", label: "Debug" },
    { value: "info", label: "Info" },
    { value: "warning", label: "Warning" },
    { value: "error", label: "Error" }
  ];
  const filteredRealTimeLogs = realTimeLogs.filter((log2) => {
    if (batchFilter && log2.batchId !== batchFilter) return false;
    if (levelFilter && log2.level !== levelFilter) return false;
    if (searchFilter && !log2.message.toLowerCase().includes(searchFilter.toLowerCase()))
      return false;
    return true;
  });
  const displayLogs = showHistorical ? (historicalLogs == null ? void 0 : historicalLogs.items) ?? [] : filteredRealTimeLogs;
  const handleExport = () => {
    const logs = displayLogs;
    const data = logs.map((log2) => ({
      timestamp: new Date(log2.timestamp).toISOString(),
      batchId: log2.batchId,
      level: log2.level,
      message: log2.message
    }));
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `logs_${(/* @__PURE__ */ new Date()).toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(FileText, { className: "w-6 h-6 text-brand-500" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: "Logs" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center gap-2", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
        Button,
        {
          variant: showHistorical ? "secondary" : "primary",
          size: "sm",
          onClick: () => setShowHistorical(!showHistorical),
          children: showHistorical ? "Real-time" : "Historical"
        }
      ) })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mb-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Filter, { className: "w-4 h-4", style: { color: "var(--color-text-secondary)" } }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: "Filters" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Select,
          {
            options: batchOptions,
            value: batchFilter,
            onChange: (e) => setBatchFilter(e.target.value)
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Select,
          {
            options: levelOptions2,
            value: levelFilter,
            onChange: (e) => setLevelFilter(e.target.value)
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Input,
          {
            placeholder: "Search logs...",
            value: searchFilter,
            onChange: (e) => setSearchFilter(e.target.value)
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
          !showHistorical && /* @__PURE__ */ jsxRuntimeExports.jsx(
            Button,
            {
              variant: "ghost",
              size: "sm",
              onClick: () => setAutoScroll(!autoScroll),
              title: autoScroll ? "Pause auto-scroll" : "Resume auto-scroll",
              children: autoScroll ? /* @__PURE__ */ jsxRuntimeExports.jsx(Pause, { className: "w-4 h-4" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-4 h-4" })
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: handleExport, title: "Export logs", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Download, { className: "w-4 h-4" }) }),
          !showHistorical && /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: clearLogs, title: "Clear logs", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Trash2, { className: "w-4 h-4" }) })
        ] })
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between p-3 border-b", style: { borderColor: "var(--color-border-default)" }, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: showHistorical ? `Historical Logs (${(historicalLogs == null ? void 0 : historicalLogs.total) ?? 0} total)` : `Real-time Logs (${filteredRealTimeLogs.length} entries)` }),
        !showHistorical && !autoScroll && /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs text-yellow-400", children: "Auto-scroll paused" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "div",
        {
          ref: logContainerRef,
          className: "h-[500px] overflow-y-auto font-mono text-sm",
          children: historicalLoading ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-center h-full", children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "lg" }) }) : displayLogs.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-center h-full", style: { color: "var(--color-text-tertiary)" }, children: showHistorical ? "No logs found" : "No logs yet. Waiting for activity..." }) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "p-2", children: displayLogs.map((log2, index) => /* @__PURE__ */ jsxRuntimeExports.jsx(LogEntryRow$1, { log: log2, showBatchId: true }, log2.id ?? index)) })
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-4 text-xs", style: { color: "var(--color-text-secondary)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Log Levels:" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex items-center gap-1", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "w-2 h-2 rounded-full bg-zinc-500" }),
        "Debug"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex items-center gap-1", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "w-2 h-2 rounded-full bg-blue-500" }),
        "Info"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex items-center gap-1", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "w-2 h-2 rounded-full bg-yellow-500" }),
        "Warning"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex items-center gap-1", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "w-2 h-2 rounded-full bg-red-500" }),
        "Error"
      ] })
    ] })
  ] });
}
function SettingsPage() {
  const { data: systemInfo, isLoading: infoLoading, refetch: refetchInfo } = useSystemInfo();
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useHealthStatus();
  const { data: workflowConfig, isLoading: workflowLoading, refetch: refetchWorkflow } = useWorkflowConfig();
  const updateStationInfo2 = useUpdateStationInfo();
  const updateWorkflow = useUpdateWorkflowConfig();
  const addNotification = useNotificationStore((state) => state.addNotification);
  const theme = useUIStore((state) => state.theme);
  const toggleTheme = useUIStore((state) => state.toggleTheme);
  const [isEditing, setIsEditing] = reactExports.useState(false);
  const [editForm, setEditForm] = reactExports.useState({
    id: "",
    name: "",
    description: ""
  });
  const stationId = systemInfo == null ? void 0 : systemInfo.stationId;
  const stationName = systemInfo == null ? void 0 : systemInfo.stationName;
  const stationDescription = systemInfo == null ? void 0 : systemInfo.description;
  reactExports.useEffect(() => {
    if (stationId && stationName && !isEditing) {
      setEditForm({
        id: stationId,
        name: stationName,
        description: stationDescription || ""
      });
    }
  }, [stationId, stationName, stationDescription, isEditing]);
  const handleRefresh = () => {
    refetchInfo();
    refetchHealth();
    refetchWorkflow();
  };
  const handleEditStart = () => {
    if (systemInfo) {
      setEditForm({
        id: systemInfo.stationId,
        name: systemInfo.stationName,
        description: systemInfo.description || ""
      });
    }
    setIsEditing(true);
  };
  const handleEditCancel = () => {
    setIsEditing(false);
    if (systemInfo) {
      setEditForm({
        id: systemInfo.stationId,
        name: systemInfo.stationName,
        description: systemInfo.description || ""
      });
    }
  };
  const handleEditSave = async () => {
    if (!editForm.id.trim() || !editForm.name.trim()) {
      addNotification({
        type: "error",
        title: "Validation Error",
        message: "Station ID and Name are required"
      });
      return;
    }
    try {
      await updateStationInfo2.mutateAsync({
        id: editForm.id.trim(),
        name: editForm.name.trim(),
        description: editForm.description.trim()
      });
      setIsEditing(false);
      addNotification({
        type: "success",
        title: "Success",
        message: "Station information updated successfully"
      });
    } catch (error) {
      addNotification({
        type: "error",
        title: "Update Failed",
        message: error instanceof Error ? error.message : "Failed to update station information"
      });
    }
  };
  const handleWorkflowToggle = async () => {
    if (!workflowConfig) return;
    const newEnabled = !workflowConfig.enabled;
    try {
      await updateWorkflow.mutateAsync({ enabled: newEnabled });
      addNotification({
        type: "success",
        title: newEnabled ? "Process Workflow Enabled" : "Process Workflow Disabled",
        message: newEnabled ? "WIP process start/complete is now enabled." : "WIP process start/complete is now disabled."
      });
    } catch (error) {
      addNotification({
        type: "error",
        title: "Update Failed",
        message: error instanceof Error ? error.message : "Failed to update workflow configuration"
      });
    }
  };
  const handleWipInputModeChange = async (mode) => {
    try {
      await updateWorkflow.mutateAsync({ input_mode: mode });
      addNotification({
        type: "success",
        title: "WIP Input Mode Changed",
        message: mode === "popup" ? "WIP ID will be entered manually via popup." : "WIP ID will be read from barcode scanner."
      });
    } catch (error) {
      addNotification({
        type: "error",
        title: "Update Failed",
        message: error instanceof Error ? error.message : "Failed to update workflow configuration"
      });
    }
  };
  const handleAutoSequenceStartToggle = async () => {
    if (!workflowConfig) return;
    const newValue = !workflowConfig.auto_sequence_start;
    try {
      await updateWorkflow.mutateAsync({ auto_sequence_start: newValue });
      addNotification({
        type: "success",
        title: newValue ? "Auto-start Enabled" : "Auto-start Disabled",
        message: newValue ? "Sequence will start automatically after WIP scan." : "Sequence must be started manually after WIP scan."
      });
    } catch (error) {
      addNotification({
        type: "error",
        title: "Update Failed",
        message: error instanceof Error ? error.message : "Failed to update workflow configuration"
      });
    }
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Settings, { className: "w-6 h-6 text-brand-500" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: "Settings" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "ghost", size: "sm", onClick: handleRefresh, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "w-4 h-4 mr-2" }),
        "Refresh"
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col gap-6 max-w-2xl mx-auto w-full", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Section$1,
        {
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Server, { className: "w-5 h-5" }),
          title: "Station Information",
          isLoading: infoLoading,
          action: !isEditing ? /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: handleEditStart, children: /* @__PURE__ */ jsxRuntimeExports.jsx(Pen, { className: "w-4 h-4" }) }) : null,
          children: systemInfo && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-3", children: isEditing ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              EditableRow,
              {
                label: "Station ID",
                value: editForm.id,
                onChange: (value) => setEditForm((prev) => ({ ...prev, id: value })),
                placeholder: "e.g., station_001"
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              EditableRow,
              {
                label: "Station Name",
                value: editForm.name,
                onChange: (value) => setEditForm((prev) => ({ ...prev, name: value })),
                placeholder: "e.g., Test Station 1"
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              EditableRow,
              {
                label: "Description",
                value: editForm.description,
                onChange: (value) => setEditForm((prev) => ({ ...prev, description: value })),
                placeholder: "e.g., PCB voltage testing station"
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-end gap-2 pt-2", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs(
                Button,
                {
                  variant: "ghost",
                  size: "sm",
                  onClick: handleEditCancel,
                  disabled: updateStationInfo2.isPending,
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-4 h-4 mr-1" }),
                    "Cancel"
                  ]
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsxs(
                Button,
                {
                  variant: "primary",
                  size: "sm",
                  onClick: handleEditSave,
                  disabled: updateStationInfo2.isPending,
                  children: [
                    updateStationInfo2.isPending ? /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-4 h-4 mr-1 animate-spin" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Save, { className: "w-4 h-4 mr-1" }),
                    "Save"
                  ]
                }
              )
            ] })
          ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow$1, { label: "Station ID", value: systemInfo.stationId }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow$1, { label: "Station Name", value: systemInfo.stationName }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow$1, { label: "Description", value: systemInfo.description || "-" })
          ] }) })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Section$1,
        {
          icon: (workflowConfig == null ? void 0 : workflowConfig.enabled) ? /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-5 h-5" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Pause, { className: "w-5 h-5" }),
          title: "Process Workflow",
          isLoading: workflowLoading,
          children: workflowConfig && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: "WIP Process Start/Complete" }),
                /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-1", style: { color: "var(--color-text-tertiary)" }, children: "Sync with backend MES for process tracking" })
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                ToggleSwitch,
                {
                  enabled: workflowConfig.enabled,
                  onToggle: handleWorkflowToggle,
                  disabled: updateWorkflow.isPending
                }
              )
            ] }),
            workflowConfig.enabled && /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: "WIP Input Mode" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-1", style: { color: "var(--color-text-tertiary)" }, children: "How to provide WIP ID for process tracking" })
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  "select",
                  {
                    value: workflowConfig.input_mode,
                    onChange: (e) => handleWipInputModeChange(e.target.value),
                    disabled: updateWorkflow.isPending,
                    className: "px-3 py-1.5 text-sm rounded border outline-none transition-colors cursor-pointer disabled:opacity-50",
                    style: {
                      backgroundColor: "var(--color-bg-primary)",
                      borderColor: "var(--color-border-default)",
                      color: "var(--color-text-primary)"
                    },
                    children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "popup", children: "Manual Input (Popup)" }),
                      /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "barcode", children: "Barcode Scanner" })
                    ]
                  }
                )
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: "Auto-start Sequence" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-1", style: { color: "var(--color-text-tertiary)" }, children: "Start sequence automatically after WIP scan" })
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  ToggleSwitch,
                  {
                    enabled: workflowConfig.auto_sequence_start,
                    onToggle: handleAutoSequenceStartToggle,
                    disabled: updateWorkflow.isPending
                  }
                )
              ] })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "div",
              {
                className: "text-xs p-2 rounded",
                style: {
                  backgroundColor: workflowConfig.enabled ? "rgba(62, 207, 142, 0.1)" : "var(--color-bg-tertiary)",
                  color: workflowConfig.enabled ? "var(--color-brand-500)" : "var(--color-text-tertiary)"
                },
                children: workflowConfig.enabled ? "Enabled: Automatically calls process start/complete API during sequence execution." : "Disabled: Runs sequence only without process tracking."
              }
            )
          ] })
        }
      ),
      (workflowConfig == null ? void 0 : workflowConfig.enabled) && (workflowConfig == null ? void 0 : workflowConfig.input_mode) === "barcode" && /* @__PURE__ */ jsxRuntimeExports.jsx(
        Section$1,
        {
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(ScanBarcode, { className: "w-5 h-5" }),
          title: "Barcode Scanner",
          children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Type" }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "select",
                {
                  value: "serial",
                  disabled: true,
                  className: "px-3 py-1.5 text-sm rounded border outline-none transition-colors cursor-not-allowed opacity-60",
                  style: {
                    backgroundColor: "var(--color-bg-primary)",
                    borderColor: "var(--color-border-default)",
                    color: "var(--color-text-primary)"
                  },
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "serial", children: "Serial (COM Port)" }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "usb_hid", children: "USB HID" }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "keyboard_wedge", children: "Keyboard Wedge" })
                  ]
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Port" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "input",
                {
                  type: "text",
                  value: "COM3",
                  disabled: true,
                  placeholder: "e.g., COM3 or /dev/ttyUSB0",
                  className: "px-3 py-1.5 text-sm rounded border outline-none transition-colors cursor-not-allowed opacity-60",
                  style: {
                    backgroundColor: "var(--color-bg-primary)",
                    borderColor: "var(--color-border-default)",
                    color: "var(--color-text-primary)",
                    width: "140px"
                  }
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Baudrate" }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "select",
                {
                  value: "9600",
                  disabled: true,
                  className: "px-3 py-1.5 text-sm rounded border outline-none transition-colors cursor-not-allowed opacity-60",
                  style: {
                    backgroundColor: "var(--color-bg-primary)",
                    borderColor: "var(--color-border-default)",
                    color: "var(--color-text-primary)"
                  },
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "9600", children: "9600" }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "19200", children: "19200" }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "38400", children: "38400" }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "115200", children: "115200" })
                  ]
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Status" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge, { status: "disconnected", size: "sm" })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "div",
              {
                className: "text-xs p-2 rounded",
                style: {
                  backgroundColor: "var(--color-bg-tertiary)",
                  color: "var(--color-text-tertiary)"
                },
                children: "Barcode scanner configuration is per-batch. Configure in batch settings for full functionality (Phase 2)."
              }
            )
          ] })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Section$1,
        {
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Cloud, { className: "w-5 h-5" }),
          title: "Backend Connection",
          isLoading: healthLoading,
          children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Status" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                StatusBadge,
                {
                  status: (health == null ? void 0 : health.backendStatus) === "connected" ? "connected" : "disconnected",
                  size: "sm"
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Backend URL" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "span",
                {
                  className: "text-sm font-mono",
                  style: { color: "var(--color-text-primary)" },
                  children: getBackendUrl()
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "div",
              {
                className: "text-xs p-2 rounded",
                style: {
                  backgroundColor: "var(--color-bg-tertiary)",
                  color: "var(--color-text-tertiary)"
                },
                children: "Backend URL is configured in station.yaml"
              }
            )
          ] })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Section$1,
        {
          icon: theme === "dark" ? /* @__PURE__ */ jsxRuntimeExports.jsx(Moon, { className: "w-5 h-5" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Sun, { className: "w-5 h-5" }),
          title: "Appearance",
          children: /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-4", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: "Theme" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-1", style: { color: "var(--color-text-tertiary)" }, children: "Switch between dark and light mode" })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "secondary", size: "sm", onClick: toggleTheme, children: theme === "dark" ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Sun, { className: "w-4 h-4 mr-2" }),
              "Light"
            ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Moon, { className: "w-4 h-4 mr-2" }),
              "Dark"
            ] }) })
          ] }) })
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "p-4 rounded-lg border max-w-2xl mx-auto w-full",
        style: {
          backgroundColor: "var(--color-bg-secondary)",
          borderColor: "var(--color-border-default)"
        },
        children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: [
          "Station Service v",
          (systemInfo == null ? void 0 : systemInfo.version) ?? "..."
        ] })
      }
    )
  ] });
}
function getBackendUrl() {
  return window.location.origin;
}
function Section$1({ icon, title, children, isLoading, action }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "p-4 rounded-lg border",
      style: {
        backgroundColor: "var(--color-bg-secondary)",
        borderColor: "var(--color-border-default)"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "h3",
            {
              className: "flex items-center gap-2 text-lg font-semibold",
              style: { color: "var(--color-text-primary)" },
              children: [
                icon,
                title
              ]
            }
          ),
          action
        ] }),
        isLoading ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "py-8 flex items-center justify-center", children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, {}) }) : children
      ]
    }
  );
}
function InfoRow$1({ label, value }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: label }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: value })
  ] });
}
function EditableRow({ label, value, onChange, placeholder }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between gap-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      "label",
      {
        className: "text-sm whitespace-nowrap",
        style: { color: "var(--color-text-secondary)" },
        children: label
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      "input",
      {
        type: "text",
        value,
        onChange: (e) => onChange(e.target.value),
        placeholder,
        className: "flex-1 px-3 py-1.5 text-sm rounded border outline-none transition-colors",
        style: {
          backgroundColor: "var(--color-bg-primary)",
          borderColor: "var(--color-border-default)",
          color: "var(--color-text-primary)"
        }
      }
    )
  ] });
}
function ToggleSwitch({ enabled, onToggle, disabled }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsx(
    "button",
    {
      onClick: onToggle,
      disabled,
      className: "relative inline-flex h-6 w-11 items-center rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
      style: {
        backgroundColor: enabled ? "var(--color-brand-500)" : "var(--color-bg-tertiary)"
      },
      children: /* @__PURE__ */ jsxRuntimeExports.jsx(
        "span",
        {
          className: "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
          style: {
            transform: enabled ? "translateX(24px)" : "translateX(4px)"
          }
        }
      )
    }
  );
}
function MonitorPage() {
  const { data: systemInfo, isLoading: infoLoading, refetch: refetchInfo } = useSystemInfo();
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useHealthStatus();
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  const lastHeartbeat = useConnectionStore((state) => state.lastHeartbeat);
  const handleRefresh = () => {
    refetchInfo();
    refetchHealth();
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Activity, { className: "w-6 h-6 text-brand-500" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: "Monitor" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "ghost", size: "sm", onClick: handleRefresh, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "w-4 h-4 mr-2" }),
        "Refresh"
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col gap-6 max-w-2xl mx-auto w-full", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Section,
        {
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Server, { className: "w-5 h-5" }),
          title: "Station Overview",
          isLoading: infoLoading,
          children: systemInfo && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-3", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow, { label: "Station ID", value: systemInfo.stationId }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow, { label: "Station Name", value: systemInfo.stationName }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow, { label: "Description", value: systemInfo.description || "-" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow, { label: "Version", value: systemInfo.version }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow, { label: "Uptime", value: formatUptime(systemInfo.uptime) })
          ] })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Section,
        {
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Wifi, { className: "w-5 h-5" }),
          title: "Connection Status",
          isLoading: healthLoading,
          children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "WebSocket" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                StatusBadge,
                {
                  status: websocketStatus === "connected" ? "connected" : "disconnected",
                  size: "sm"
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Backend" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                StatusBadge,
                {
                  status: (health == null ? void 0 : health.backendStatus) === "connected" ? "connected" : "disconnected",
                  size: "sm"
                }
              )
            ] }),
            lastHeartbeat && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between text-sm", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Last Heartbeat" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: lastHeartbeat.toLocaleTimeString() })
            ] })
          ] })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Section,
        {
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Database, { className: "w-5 h-5" }),
          title: "System Health",
          isLoading: healthLoading,
          children: health && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Overall Status" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                StatusBadge,
                {
                  status: health.status === "healthy" ? "connected" : "disconnected",
                  size: "sm"
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-1", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Batches Running" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: health.batchesRunning })
            ] }) }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-1", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Disk Usage" }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { style: { color: "var(--color-text-primary)" }, children: [
                  health.diskUsage.toFixed(1),
                  "%"
                ] })
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                ProgressBar,
                {
                  value: health.diskUsage,
                  variant: health.diskUsage > 90 ? "error" : health.diskUsage > 70 ? "warning" : "default",
                  size: "sm"
                }
              )
            ] })
          ] })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Section,
        {
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Cloud, { className: "w-5 h-5" }),
          title: "Sync Status",
          isLoading: healthLoading,
          children: health && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Backend Connection" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                StatusBadge,
                {
                  status: health.backendStatus === "connected" ? "connected" : "disconnected",
                  size: "sm"
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: "Sync queue and statistics will be displayed here when available." })
          ] })
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "p-4 rounded-lg border max-w-2xl mx-auto w-full",
        style: {
          backgroundColor: "var(--color-bg-secondary)",
          borderColor: "var(--color-border-default)"
        },
        children: /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "flex items-center justify-between text-sm",
            style: { color: "var(--color-text-tertiary)" },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
                "Station Service v",
                (systemInfo == null ? void 0 : systemInfo.version) ?? "..."
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
                "WebSocket: ",
                websocketStatus,
                " | Backend: ",
                (health == null ? void 0 : health.backendStatus) ?? "unknown"
              ] })
            ]
          }
        )
      }
    )
  ] });
}
function Section({ icon, title, children, isLoading }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "p-4 rounded-lg border",
      style: {
        backgroundColor: "var(--color-bg-secondary)",
        borderColor: "var(--color-border-default)"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-between mb-4", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "h3",
          {
            className: "flex items-center gap-2 text-lg font-semibold",
            style: { color: "var(--color-text-primary)" },
            children: [
              icon,
              title
            ]
          }
        ) }),
        isLoading ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "py-8 flex items-center justify-center", children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, {}) }) : children
      ]
    }
  );
}
function InfoRow({ label, value }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: label }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: value })
  ] });
}
function formatUptime(seconds) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor(seconds % 86400 / 3600);
  const minutes = Math.floor(seconds % 3600 / 60);
  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`;
  }
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}
function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = reactExports.useState("");
  const [password, setPassword] = reactExports.useState("");
  const [error, setError] = reactExports.useState(null);
  const operatorLogin2 = useOperatorLogin();
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!username.trim() || !password.trim()) {
      setError("Username and password are required");
      return;
    }
    try {
      await operatorLogin2.mutateAsync({
        username: username.trim(),
        password
      });
      onLoginSuccess();
    } catch (err) {
      console.error("Login error:", err);
      if (err && typeof err === "object") {
        const errorObj = err;
        if (errorObj.message) {
          setError(String(errorObj.message));
        } else if (errorObj.detail) {
          setError(String(errorObj.detail));
        } else {
          setError("Login failed. Please try again.");
        }
      } else if (err instanceof Error) {
        setError(err.message || "Login failed");
      } else {
        setError("Login failed. Please try again.");
      }
    }
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsx(
    "div",
    {
      className: "min-h-screen flex items-center justify-center p-4",
      style: { backgroundColor: "var(--color-bg-primary)" },
      children: /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "w-full max-w-md p-8 rounded-xl border",
          style: {
            backgroundColor: "var(--color-bg-secondary)",
            borderColor: "var(--color-border-default)"
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col items-center mb-8", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "div",
                {
                  className: "w-16 h-16 rounded-2xl flex items-center justify-center mb-4",
                  style: { backgroundColor: "var(--color-brand-500)" },
                  children: /* @__PURE__ */ jsxRuntimeExports.jsx(Activity, { className: "w-8 h-8 text-white" })
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "h1",
                {
                  className: "text-2xl font-bold",
                  style: { color: "var(--color-text-primary)" },
                  children: "Station UI"
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "p",
                {
                  className: "text-sm mt-1",
                  style: { color: "var(--color-text-tertiary)" },
                  children: "Sign in to continue"
                }
              )
            ] }),
            error && /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "div",
              {
                className: "flex items-center gap-2 p-3 rounded-lg mb-4",
                style: {
                  backgroundColor: "rgba(239, 68, 68, 0.1)",
                  color: "var(--color-status-error)"
                },
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(CircleAlert, { className: "w-4 h-4 flex-shrink-0" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", children: error })
                ]
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("form", { onSubmit: handleSubmit, className: "space-y-4", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "label",
                  {
                    className: "block text-sm font-medium mb-2",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Username"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "input",
                  {
                    type: "text",
                    value: username,
                    onChange: (e) => setUsername(e.target.value),
                    placeholder: "Enter your username",
                    autoFocus: true,
                    disabled: operatorLogin2.isPending,
                    className: "w-full px-4 py-3 text-sm rounded-lg border outline-none transition-colors disabled:opacity-50",
                    style: {
                      backgroundColor: "var(--color-bg-primary)",
                      borderColor: "var(--color-border-default)",
                      color: "var(--color-text-primary)"
                    }
                  }
                )
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "label",
                  {
                    className: "block text-sm font-medium mb-2",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Password"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "input",
                  {
                    type: "password",
                    value: password,
                    onChange: (e) => setPassword(e.target.value),
                    placeholder: "Enter your password",
                    disabled: operatorLogin2.isPending,
                    className: "w-full px-4 py-3 text-sm rounded-lg border outline-none transition-colors disabled:opacity-50",
                    style: {
                      backgroundColor: "var(--color-bg-primary)",
                      borderColor: "var(--color-border-default)",
                      color: "var(--color-text-primary)"
                    }
                  }
                )
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                Button,
                {
                  type: "submit",
                  variant: "primary",
                  size: "lg",
                  disabled: operatorLogin2.isPending,
                  className: "w-full mt-6",
                  children: operatorLogin2.isPending ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-4 h-4 mr-2 animate-spin" }),
                    "Signing in..."
                  ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(LogIn, { className: "w-4 h-4 mr-2" }),
                    "Sign In"
                  ] })
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "p",
              {
                className: "text-xs text-center mt-6",
                style: { color: "var(--color-text-tertiary)" },
                children: "Use your MES account credentials"
              }
            )
          ]
        }
      )
    }
  );
}
function AppContent() {
  usePollingFallback();
  const { data: operatorSession, isLoading: sessionLoading, refetch: refetchSession } = useOperatorSession();
  const theme = useUIStore((state) => state.theme);
  reactExports.useEffect(() => {
    document.documentElement.classList.remove("dark", "light");
    document.documentElement.classList.add(theme);
  }, [theme]);
  if (sessionLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "min-h-screen flex items-center justify-center",
        style: { backgroundColor: "var(--color-bg-primary)" },
        children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "lg" })
      }
    );
  }
  if (!(operatorSession == null ? void 0 : operatorSession.loggedIn)) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(LoginPage, { onLoginSuccess: () => refetchSession() });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsx(ErrorBoundary, { children: /* @__PURE__ */ jsxRuntimeExports.jsx(Layout, { children: /* @__PURE__ */ jsxRuntimeExports.jsxs(Routes, { children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.DASHBOARD, element: /* @__PURE__ */ jsxRuntimeExports.jsx(DashboardPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.BATCHES, element: /* @__PURE__ */ jsxRuntimeExports.jsx(BatchesPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.BATCH_DETAIL, element: /* @__PURE__ */ jsxRuntimeExports.jsx(BatchDetailPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.SEQUENCES, element: /* @__PURE__ */ jsxRuntimeExports.jsx(SequencesPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.SEQUENCE_DETAIL, element: /* @__PURE__ */ jsxRuntimeExports.jsx(SequencesPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.MANUAL, element: /* @__PURE__ */ jsxRuntimeExports.jsx(ManualControlPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.LOGS, element: /* @__PURE__ */ jsxRuntimeExports.jsx(LogsPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.MONITOR, element: /* @__PURE__ */ jsxRuntimeExports.jsx(MonitorPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.SETTINGS, element: /* @__PURE__ */ jsxRuntimeExports.jsx(SettingsPage, {}) })
  ] }) }) });
}
function App() {
  return /* @__PURE__ */ jsxRuntimeExports.jsx(AppContent, {});
}
clientExports.createRoot(document.getElementById("root")).render(
  /* @__PURE__ */ jsxRuntimeExports.jsx(reactExports.StrictMode, { children: /* @__PURE__ */ jsxRuntimeExports.jsx(ErrorBoundary, { children: /* @__PURE__ */ jsxRuntimeExports.jsx(QueryClientProvider, { client: queryClient, children: /* @__PURE__ */ jsxRuntimeExports.jsx(WebSocketProvider, { children: /* @__PURE__ */ jsxRuntimeExports.jsx(BrowserRouter, { basename: "/ui", children: /* @__PURE__ */ jsxRuntimeExports.jsx(App, {}) }) }) }) }) })
);
