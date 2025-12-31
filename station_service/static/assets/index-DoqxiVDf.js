var __defProp = Object.defineProperty;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __publicField = (obj, key, value) => __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);
import { j as jsxRuntimeExports, Q as QueryClient, u as useQuery, a as useQueryClient, b as useMutation, c as QueryClientProvider } from "./query-nDuVABiU.js";
import { b as requireReactDom, a as reactExports, u as useLocation, N as NavLink, R as React, c as useNavigate, d as useParams, e as Routes, f as Route, B as BrowserRouter } from "./vendor-Br0po5n5.js";
import { c as create } from "./state-CkuP8Qb0.js";
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
const LoaderCircle = createLucideIcon("LoaderCircle", [
  ["path", { d: "M21 12a9 9 0 1 1-6.219-8.56", key: "13zald" }]
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
const Monitor = createLucideIcon("Monitor", [
  ["rect", { width: "20", height: "14", x: "2", y: "3", rx: "2", key: "48i651" }],
  ["line", { x1: "8", x2: "16", y1: "21", y2: "21", key: "1svkeh" }],
  ["line", { x1: "12", x2: "12", y1: "17", y2: "21", key: "vw1qmm" }]
]);
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
const Timer = createLucideIcon("Timer", [
  ["line", { x1: "10", x2: "14", y1: "2", y2: "2", key: "14vaq8" }],
  ["line", { x1: "12", x2: "15", y1: "14", y2: "11", key: "17fdiu" }],
  ["circle", { cx: "12", cy: "14", r: "8", key: "1e1u0o" }]
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
      console.info("Cleaned up legacy local batch data:", removedKeys);
    }
  } catch (e) {
    console.warn("Failed to cleanup legacy local batches:", e);
  }
}
cleanupLegacyLocalBatches();
const useBatchStore = create((set, get) => ({
  // Initial state
  batches: /* @__PURE__ */ new Map(),
  selectedBatchId: null,
  batchStatistics: /* @__PURE__ */ new Map(),
  isWizardOpen: false,
  // Actions
  setBatches: (batches2) => set({
    batches: new Map(batches2.map((b) => [b.id, b]))
  }),
  updateBatch: (batch) => set((state) => {
    const newBatches = new Map(state.batches);
    newBatches.set(batch.id, batch);
    return { batches: newBatches };
  }),
  removeBatch: (batchId) => set((state) => {
    const newBatches = new Map(state.batches);
    newBatches.delete(batchId);
    const newStats = new Map(state.batchStatistics);
    newStats.delete(batchId);
    return { batches: newBatches, batchStatistics: newStats };
  }),
  updateBatchStatus: (batchId, status) => set((state) => {
    const batch = state.batches.get(batchId);
    if (!batch) return state;
    const newBatches = new Map(state.batches);
    newBatches.set(batchId, { ...batch, status });
    return { batches: newBatches };
  }),
  setLastRunResult: (batchId, passed) => set((state) => {
    const batch = state.batches.get(batchId);
    if (!batch) return state;
    const newBatches = new Map(state.batches);
    newBatches.set(batchId, { ...batch, lastRunPassed: passed });
    return { batches: newBatches };
  }),
  updateStepProgress: (batchId, currentStep, stepIndex, progress) => set((state) => {
    const batch = state.batches.get(batchId);
    if (!batch) return state;
    const newBatches = new Map(state.batches);
    newBatches.set(batchId, {
      ...batch,
      currentStep,
      stepIndex,
      progress
    });
    return { batches: newBatches };
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
    return { batches: newBatches };
  }),
  selectBatch: (batchId) => set({ selectedBatchId: batchId }),
  clearBatches: () => set({ batches: /* @__PURE__ */ new Map() }),
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
    const current = newStats.get(batchId) || { total: 0, pass: 0, fail: 0 };
    const updated = {
      total: current.total + 1,
      pass: passed ? current.pass + 1 : current.pass,
      fail: passed ? current.fail : current.fail + 1,
      passRate: 0
    };
    updated.passRate = updated.total > 0 ? updated.pass / updated.total : 0;
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
    const total = { total: 0, pass: 0, fail: 0, passRate: 0 };
    batchStatistics.forEach((s) => {
      total.total += s.total;
      total.pass += s.pass;
      total.fail += s.fail;
    });
    total.passRate = total.total > 0 ? total.pass / total.total : 0;
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
  addLog: (log) => set((state) => {
    const newLogs = [...state.logs, log];
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
    return logs.filter((log) => {
      if (filters.batchId && log.batchId !== filters.batchId) {
        return false;
      }
      if (filters.level && log.level !== filters.level) {
        return false;
      }
      if (filters.search && !log.message.toLowerCase().includes(filters.search.toLowerCase())) {
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
function generateId() {
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
          id: generateId(),
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
function formatTimestamp(date) {
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
                children: formatTimestamp(notification.timestamp)
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
  const location = useLocation();
  const { theme, toggleTheme } = useUIStore();
  const { isOpen, togglePanel, getUnreadCount } = useNotificationStore();
  const isDark = theme === "dark";
  const unreadCount = getUnreadCount();
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
  // Batches
  batches: ["batches"],
  batch: (id) => ["batches", id],
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
function snakeToCamel$1(str) {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}
function transformKeys$1(obj) {
  if (obj === null || obj === void 0) {
    return obj;
  }
  if (Array.isArray(obj)) {
    return obj.map((item) => transformKeys$1(item));
  }
  if (typeof obj === "object") {
    const transformed = {};
    for (const [key, value] of Object.entries(obj)) {
      transformed[snakeToCamel$1(key)] = transformKeys$1(value);
    }
    return transformed;
  }
  return obj;
}
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
    if (response.data) {
      response.data = transformKeys$1(response.data);
    }
    return response;
  },
  (error) => {
    var _a, _b, _c;
    const status = (_a = error.response) == null ? void 0 : _a.status;
    if ((_c = (_b = error.response) == null ? void 0 : _b.data) == null ? void 0 : _c.error) {
      return Promise.reject({
        ...error.response.data.error,
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
  getBatches,
  manualControl,
  startBatch,
  startSequence,
  stopBatch,
  stopSequence
}, Symbol.toStringTag, { value: "Module" }));
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
  return useQuery({
    queryKey: queryKeys.batch(batchId ?? ""),
    queryFn: () => getBatch(batchId),
    enabled: !!batchId,
    refetchInterval: POLLING_INTERVALS.batchDetail
    // Poll every 1 second for step updates
  });
}
function useStartBatch() {
  const queryClient2 = useQueryClient();
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
    onSuccess: (result) => {
      queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
      if ("status" in result && result.status === "already_running") ;
      else {
        toast.success("Batch started successfully");
      }
    },
    onError: (error) => {
      toast.error(`Failed to start batch: ${getErrorMessage(error)}`);
    }
  });
}
function useStopBatch() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (batchId) => stopBatch(batchId),
    onSuccess: () => {
      queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success("Batch stopped successfully");
    },
    onError: (error) => {
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
    onSuccess: (result, variables) => {
      queryClient2.invalidateQueries({ queryKey: queryKeys.batch(variables.batchId) });
      queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
      if ("status" in result && result.status === "already_running") ;
      else {
        toast.success("Sequence started successfully");
      }
    },
    onError: (error) => {
      toast.error(`Failed to start sequence: ${getErrorMessage(error)}`);
    }
  });
}
function useStopSequence() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (batchId) => stopSequence(batchId),
    onSuccess: (_, batchId) => {
      queryClient2.invalidateQueries({ queryKey: queryKeys.batch(batchId) });
      queryClient2.invalidateQueries({ queryKey: queryKeys.batches });
      toast.success("Sequence stopped successfully");
    },
    onError: (error) => {
      toast.error(`Failed to stop sequence: ${getErrorMessage(error)}`);
    }
  });
}
function useManualControl() {
  return useMutation({
    mutationFn: ({
      batchId,
      request
    }) => manualControl(batchId, request),
    onSuccess: () => {
      toast.success("Command executed successfully");
    },
    onError: (error) => {
      toast.error(`Command failed: ${getErrorMessage(error)}`);
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
function useAllBatchStatistics() {
  return useQuery({
    queryKey: ["allBatchStatistics"],
    queryFn: getAllBatchStatistics,
    staleTime: 30 * 1e3,
    // 30 seconds
    retry: false,
    // Don't retry on 404
    throwOnError: false
    // Don't throw errors
  });
}
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
const WebSocketContext = reactExports.createContext(null);
function generateLogId() {
  return Date.now() * 1e3 + Math.floor(Math.random() * 1e3);
}
function getWebSocketUrl(path) {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host;
  return `${protocol}//${host}${path}`;
}
function snakeToCamel(str) {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}
function transformKeys(obj) {
  if (obj === null || obj === void 0) {
    return obj;
  }
  if (Array.isArray(obj)) {
    return obj.map((item) => transformKeys(item));
  }
  if (typeof obj === "object") {
    const transformed = {};
    for (const [key, value] of Object.entries(obj)) {
      transformed[snakeToCamel(key)] = transformKeys(value);
    }
    return transformed;
  }
  return obj;
}
function WebSocketProvider({ children, url = "/ws" }) {
  const queryClient2 = useQueryClient();
  const socketRef = reactExports.useRef(null);
  const subscribedBatchIds = reactExports.useRef(/* @__PURE__ */ new Set());
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
  const addLog = useLogStore((s) => s.addLog);
  const addNotification = useNotificationStore((s) => s.addNotification);
  const handleMessage = reactExports.useCallback(
    (message) => {
      switch (message.type) {
        case "batch_status": {
          updateBatchStatus(message.batchId, message.data.status);
          if (message.data.currentStep !== void 0) {
            updateStepProgress(
              message.batchId,
              message.data.currentStep,
              message.data.stepIndex,
              message.data.progress
            );
          }
          break;
        }
        case "step_start": {
          updateStepProgress(
            message.batchId,
            message.data.step,
            message.data.index,
            message.data.index / message.data.total
          );
          break;
        }
        case "step_complete": {
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
          updateBatchStatus(message.batchId, "completed");
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
          addLog({
            id: generateLogId(),
            batchId: message.batchId,
            level: "error",
            message: `[${message.data.code}] ${message.data.message}${message.data.step ? ` (step: ${message.data.step})` : ""}`,
            timestamp: new Date(message.data.timestamp)
          });
          addNotification({
            type: "error",
            title: `Error: ${message.data.code}`,
            message: message.data.message,
            batchId: message.batchId
          });
          break;
        }
        case "subscribed":
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
    [updateBatchStatus, updateStepProgress, setLastRunResult, incrementBatchStats, addLog, addNotification, queryClient2]
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
      if (subscribedBatchIds.current.size > 0) {
        const message = {
          type: "subscribe",
          batchIds: Array.from(subscribedBatchIds.current)
        };
        socket.send(JSON.stringify(message));
      }
    };
    socket.onmessage = (event) => {
      updateHeartbeat();
      try {
        const rawData = JSON.parse(event.data);
        const data = transformKeys(rawData);
        handleMessage(data);
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
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
    var _a;
    batchIds.forEach((id) => subscribedBatchIds.current.add(id));
    if (((_a = socketRef.current) == null ? void 0 : _a.readyState) === WebSocket.OPEN) {
      const message = {
        type: "subscribe",
        batchIds
      };
      socketRef.current.send(JSON.stringify(message));
    }
  }, []);
  const unsubscribe = reactExports.useCallback((batchIds) => {
    var _a;
    batchIds.forEach((id) => subscribedBatchIds.current.delete(id));
    if (((_a = socketRef.current) == null ? void 0 : _a.readyState) === WebSocket.OPEN) {
      const message = {
        type: "unsubscribe",
        batchIds
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
        ] })
      ]
    }
  );
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
function LogEntryRow({ log, showBatchId = true }) {
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    });
  };
  const styles = levelStyles[log.level];
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
            children: formatTime(log.timestamp)
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "span",
          {
            className: "px-1.5 py-0.5 rounded text-xs uppercase w-16 text-center flex-shrink-0",
            style: { backgroundColor: styles.badge, color: styles.badgeText },
            children: log.level
          }
        ),
        showBatchId && log.batchId && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex-shrink-0", style: { color: "var(--color-text-tertiary)" }, children: [
          "[",
          log.batchId,
          "]"
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "flex-1 break-all", style: { color: styles.text }, children: log.message })
      ]
    }
  );
}
const variantColors = {
  default: "var(--color-brand-500)",
  success: "#22c55e",
  warning: "#f59e0b",
  error: "#ef4444"
};
const sizeClasses$1 = {
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
        className: `w-full rounded-full overflow-hidden ${sizeClasses$1[size]}`,
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
const sizeClasses = {
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
      className: `inline-flex items-center gap-1.5 rounded-full font-medium ${sizeClasses[size]} ${className}`,
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
    const total = { total: 0, pass: 0, fail: 0, passRate: 0 };
    batchStatistics.forEach((s) => {
      total.total += s.total;
      total.pass += s.pass;
      total.fail += s.fail;
    });
    total.passRate = total.total > 0 ? total.pass / total.total : 0;
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
          value: totalStats.pass,
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
          logs.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: "No recent activity" }) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-1 max-h-64 overflow-y-auto", children: logs.slice().reverse().map((log) => /* @__PURE__ */ jsxRuntimeExports.jsx(LogEntryRow, { log, showBatchId: true }, log.id)) })
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
  const stats = statistics || { total: 0, pass: 0, fail: 0, passRate: 0 };
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
              value: stats.pass,
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
function BatchList({ batches: batches2, statistics, onStart, onStop, onDelete, onSelect, isLoading }) {
  const { batchId: selectedBatchId } = useParams();
  const [statusFilter, setStatusFilter] = reactExports.useState("all");
  const batchStatistics = useBatchStore(useShallow((state) => state.batchStatistics));
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
    totalStats.pass += stats.pass;
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
      StatCard$1,
      {
        icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Layers, { className: "w-5 h-5" }),
        label: "Total Executions",
        value: totalStats.total,
        color: "text-zinc-400",
        bgColor: "bg-zinc-700/50"
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      StatCard$1,
      {
        icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-5 h-5" }),
        label: "Passed",
        value: totalStats.pass,
        color: "text-green-500",
        bgColor: "bg-green-500/10"
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      StatCard$1,
      {
        icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-5 h-5" }),
        label: "Failed",
        value: totalStats.fail,
        color: "text-red-500",
        bgColor: "bg-red-500/10"
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      StatCard$1,
      {
        icon: /* @__PURE__ */ jsxRuntimeExports.jsx(TrendingUp, { className: "w-5 h-5" }),
        label: "Pass Rate",
        value: totalStats.total > 0 ? `${(totalStats.passRate * 100).toFixed(1)}%` : "-",
        color: totalStats.passRate >= 0.9 ? "text-green-500" : totalStats.passRate >= 0.7 ? "text-yellow-500" : totalStats.passRate > 0 ? "text-red-500" : "text-zinc-400",
        bgColor: totalStats.passRate >= 0.9 ? "bg-green-500/10" : totalStats.passRate >= 0.7 ? "bg-yellow-500/10" : totalStats.passRate > 0 ? "bg-red-500/10" : "bg-zinc-700/50"
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      StatCard$1,
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
function StatCard$1({
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
  const { subscribe, unsubscribe, isConnected } = useWebSocket();
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  const isServerConnected = isConnected && websocketStatus === "connected";
  const batchesMap = useBatchStore(useShallow((state) => state.batches));
  const batchStatistics = useBatchStore(useShallow((state) => state.batchStatistics));
  const isWizardOpen = useBatchStore((state) => state.isWizardOpen);
  const openWizard = useBatchStore((state) => state.openWizard);
  const closeWizard = useBatchStore((state) => state.closeWizard);
  const storeBatches = reactExports.useMemo(() => {
    return Array.from(batchesMap.values());
  }, [batchesMap]);
  const startBatch2 = useStartBatch();
  const stopBatch2 = useStopBatch();
  const deleteBatch2 = useDeleteBatch();
  const createBatches2 = useCreateBatches();
  reactExports.useEffect(() => {
    if (batches2 && batches2.length > 0) {
      const batchIds = batches2.map((b) => b.id);
      subscribe(batchIds);
      return () => unsubscribe(batchIds);
    }
  }, [batches2, subscribe, unsubscribe]);
  const displayBatches = storeBatches.length > 0 ? storeBatches : batches2 ?? [];
  const handleSelectBatch = (id) => {
    navigate(getBatchDetailRoute(id));
  };
  const handleStartBatch = async (id) => {
    await startBatch2.mutateAsync(id);
  };
  const handleStopBatch = async (id) => {
    await stopBatch2.mutateAsync(id);
  };
  const handleCreateBatches = async (request) => {
    await createBatches2.mutateAsync(request);
    closeWizard();
  };
  const handleDeleteBatch = async (id) => {
    if (window.confirm("Are you sure you want to delete this batch?")) {
      await deleteBatch2.mutateAsync(id);
    }
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
        onStart: handleStartBatch,
        onStop: handleStopBatch,
        onDelete: handleDeleteBatch,
        onSelect: handleSelectBatch,
        isLoading: startBatch2.isPending || stopBatch2.isPending || deleteBatch2.isPending
      }
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
function isBatchDetail$1(batch) {
  return "parameters" in batch && "hardwareStatus" in batch;
}
function BatchDetailPage() {
  const { batchId } = useParams();
  const navigate = useNavigate();
  const { data: batch, isLoading } = useBatch(batchId ?? null);
  const { subscribe, unsubscribe } = useWebSocket();
  const getBatchStats = useBatchStore((state) => state.getBatchStats);
  const startBatch2 = useStartBatch();
  const startSequence2 = useStartSequence();
  const stopSequence2 = useStopSequence();
  const stopBatch2 = useStopBatch();
  reactExports.useEffect(() => {
    if (batchId) {
      subscribe([batchId]);
      return () => unsubscribe([batchId]);
    }
  }, [batchId, subscribe, unsubscribe]);
  const statistics = reactExports.useMemo(() => {
    return batchId ? getBatchStats(batchId) : void 0;
  }, [batchId, getBatchStats]);
  const steps = reactExports.useMemo(() => {
    var _a;
    if (!batch) return [];
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
      console.error("[handleStartSequence] Missing batchId or batch");
      return;
    }
    try {
      console.log("[handleStartSequence] Starting sequence for batch:", batchId, "status:", batch.status);
      if (batch.status === "idle") {
        console.log("[handleStartSequence] Starting batch first...");
        await startBatch2.mutateAsync(batchId);
        console.log("[handleStartSequence] Batch started");
      }
      console.log("[handleStartSequence] Starting sequence...");
      await startSequence2.mutateAsync({ batchId, request: void 0 });
      console.log("[handleStartSequence] Sequence started successfully");
    } catch (error) {
      console.error("[handleStartSequence] Error:", error);
    }
  };
  const handleStopSequence = async () => {
    if (batchId) {
      await stopSequence2.mutateAsync(batchId);
      await stopBatch2.mutateAsync(batchId);
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
  const isRunning = batch.status === "running" || batch.status === "starting";
  const canStart = batch.status === "idle" || batch.status === "completed" || batch.status === "error";
  const totalStepsTime = steps.reduce((sum, step) => sum + (step.duration || 0), 0);
  const elapsedTime = isBatchDetail$1(batch) && batch.execution ? batch.execution.elapsed : batch.elapsed;
  const progress = isBatchDetail$1(batch) && batch.execution ? batch.execution.progress : batch.progress;
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
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-h-full p-6 space-y-6", style: { backgroundColor: "var(--color-bg-primary)" }, children: [
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
        /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge, { status: batch.status })
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
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-6", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-lg p-6 border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mb-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Layers, { className: "w-5 h-5 text-brand-500" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: "Execution Statistics" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-2 gap-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            StatCard,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-5 h-5", style: { color: "var(--color-text-secondary)" } }),
              label: "Total Runs",
              value: (statistics == null ? void 0 : statistics.total) ?? 0
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            StatCard,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-5 h-5 text-green-500" }),
              label: "Pass",
              value: (statistics == null ? void 0 : statistics.pass) ?? 0,
              color: "#4ade80"
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            StatCard,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-5 h-5 text-red-500" }),
              label: "Fail",
              value: (statistics == null ? void 0 : statistics.fail) ?? 0,
              color: "#f87171"
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            StatCard,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleAlert, { className: "w-5 h-5 text-brand-500" }),
              label: "Pass Rate",
              value: `${(((statistics == null ? void 0 : statistics.passRate) ?? 0) * 100).toFixed(1)}%`,
              color: "var(--color-brand-500)"
            }
          )
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-lg p-6 border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mb-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Timer, { className: "w-5 h-5 text-brand-500" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: "Timing & Result" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-2 gap-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            StatCard,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-5 h-5", style: { color: "var(--color-text-secondary)" } }),
              label: "Total Elapsed",
              value: `${elapsedTime.toFixed(1)}s`
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            StatCard,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Timer, { className: "w-5 h-5", style: { color: "var(--color-text-secondary)" } }),
              label: "Steps Time",
              value: `${totalStepsTime.toFixed(2)}s`
            }
          )
        ] }),
        verdict && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-4 p-4 rounded-lg flex items-center justify-center gap-3", style: { backgroundColor: "var(--color-bg-tertiary)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: verdict.color, children: verdict.icon }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: `text-2xl font-bold ${verdict.color}`, children: verdict.text })
        ] })
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-lg p-6 border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mb-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-5 h-5 text-brand-500" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: "Step Results" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(StepsTable, { steps, totalSteps: batch.totalSteps ?? 0, stepNames: batch.stepNames })
    ] })
  ] });
}
function MetaCard({ label, value }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-3 rounded-lg", style: { backgroundColor: "var(--color-bg-tertiary)" }, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs mb-1", style: { color: "var(--color-text-tertiary)" }, children: label }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm font-medium truncate", style: { color: "var(--color-text-primary)" }, children: value })
  ] });
}
function StatCard({
  icon,
  label,
  value,
  color
}) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-3 rounded-lg flex items-center gap-3", style: { backgroundColor: "var(--color-bg-tertiary)" }, children: [
    icon,
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: label }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-lg font-semibold", style: { color: color || "var(--color-text-primary)" }, children: value })
    ] })
  ] });
}
function StepsTable({ steps, totalSteps, stepNames }) {
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
    /* @__PURE__ */ jsxRuntimeExports.jsx("tbody", { children: displaySteps.map((step) => /* @__PURE__ */ jsxRuntimeExports.jsx(StepRow, { step }, `${step.order}-${step.name}`)) })
  ] }) });
}
function StepRow({ step }) {
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
      className: "border-b transition-colors",
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
  const [selectedFile, setSelectedFile] = reactExports.useState(null);
  const [validationResult, setValidationResult] = reactExports.useState(null);
  const [forceOverwrite, setForceOverwrite] = reactExports.useState(false);
  const fileInputRef = reactExports.useRef(null);
  const validateMutation = useValidateSequence();
  const { mutate: upload, progress, isPending, resetProgress } = useUploadSequence();
  const handleDragOver = reactExports.useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);
  const handleDragLeave = reactExports.useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);
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
    []
  );
  const handleFileInputChange = reactExports.useCallback(
    async (e) => {
      const files = e.target.files;
      const file = files == null ? void 0 : files[0];
      if (file) {
        await handleFileSelect(file);
      }
    },
    []
  );
  const handleFileSelect = reactExports.useCallback(
    async (file) => {
      if (!file.name.endsWith(".zip")) {
        setValidationResult({
          valid: false,
          errors: [{ field: "file", message: "Only .zip files are supported" }]
        });
        return;
      }
      setSelectedFile(file);
      setValidationResult(null);
      resetProgress();
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
    [validateMutation, resetProgress]
  );
  const handleUpload = reactExports.useCallback(() => {
    if (!selectedFile || !(validationResult == null ? void 0 : validationResult.valid)) return;
    upload(
      { file: selectedFile, force: forceOverwrite },
      {
        onSuccess: () => {
          onSuccess == null ? void 0 : onSuccess();
        }
      }
    );
  }, [selectedFile, validationResult, forceOverwrite, upload, onSuccess]);
  const handleReset = reactExports.useCallback(() => {
    setSelectedFile(null);
    setValidationResult(null);
    setForceOverwrite(false);
    resetProgress();
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, [resetProgress]);
  const handleBrowse = reactExports.useCallback(() => {
    var _a;
    (_a = fileInputRef.current) == null ? void 0 : _a.click();
  }, []);
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-semibold text-white", children: "Upload Sequence Package" }),
      onClose && /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: onClose, children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-4 h-4" }) })
    ] }),
    !selectedFile && /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        onDragOver: handleDragOver,
        onDragLeave: handleDragLeave,
        onDrop: handleDrop,
        className: `border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${isDragOver ? "border-brand-500 bg-brand-500/10" : "border-zinc-600 hover:border-zinc-500"}`,
        onClick: handleBrowse,
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
          /* @__PURE__ */ jsxRuntimeExports.jsx(Upload, { className: "w-12 h-12 mx-auto text-zinc-500 mb-4" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-zinc-300 mb-2", children: "Drag and drop a sequence package here" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-zinc-500", children: "or click to browse" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-zinc-600 mt-4", children: "Supported format: .zip" })
        ]
      }
    ),
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
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "text-xs text-zinc-500 space-y-1", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-medium text-zinc-400", children: "Package Requirements:" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("ul", { className: "list-disc list-inside space-y-0.5", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("li", { children: "Must be a valid ZIP archive" }),
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
function ManualControlPage() {
  const { data: batches2, isLoading } = useBatchList();
  const [selectedBatchId, setSelectedBatchId] = reactExports.useState("");
  const { data: batchDetail } = useBatch(selectedBatchId || null);
  const [selectedHardware, setSelectedHardware] = reactExports.useState("");
  const [command, setCommand] = reactExports.useState("");
  const [params, setParams] = reactExports.useState("{}");
  const [commandHistory, setCommandHistory] = reactExports.useState([]);
  const [lastResult, setLastResult] = reactExports.useState(null);
  const manualControl2 = useManualControl();
  const handleExecute = async () => {
    if (!selectedBatchId || !selectedHardware || !command) return;
    try {
      const parsedParams = JSON.parse(params);
      const request = {
        hardware: selectedHardware,
        command,
        params: parsedParams
      };
      const result = await manualControl2.mutateAsync({
        batchId: selectedBatchId,
        request
      });
      setLastResult(result);
      setCommandHistory((prev) => [
        {
          id: Date.now(),
          batchId: selectedBatchId,
          hardware: selectedHardware,
          command,
          params: parsedParams,
          result: result.result,
          timestamp: /* @__PURE__ */ new Date(),
          success: true
        },
        ...prev.slice(0, 19)
        // Keep last 20 commands
      ]);
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      setCommandHistory((prev) => [
        {
          id: Date.now(),
          batchId: selectedBatchId,
          hardware: selectedHardware,
          command,
          params: JSON.parse(params),
          result: { error: errorMessage },
          timestamp: /* @__PURE__ */ new Date(),
          success: false
        },
        ...prev.slice(0, 19)
      ]);
    }
  };
  const batchOptions = (batches2 == null ? void 0 : batches2.map((b) => ({
    value: b.id,
    label: `${b.name} (${b.status})`
  }))) ?? [];
  const hardwareOptions = isBatchDetail(batchDetail) && batchDetail.hardwareStatus ? Object.entries(batchDetail.hardwareStatus).map(([id, status]) => ({
    value: id,
    label: `${id} (${status.status})`
  })) : [];
  if (isLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingOverlay, { message: "Loading batches..." });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(Wrench, { className: "w-6 h-6 text-brand-500" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: "Manual Control" })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-5 h-5 text-yellow-500" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-yellow-400 text-sm", children: "Manual control mode. Use with caution - direct hardware access can affect system state." })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 rounded-lg border space-y-4", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("h3", { className: "text-lg font-semibold flex items-center gap-2", style: { color: "var(--color-text-primary)" }, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Send, { className: "w-5 h-5" }),
            "Command Executor"
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Select,
            {
              label: "Batch",
              options: batchOptions,
              value: selectedBatchId,
              onChange: (e) => {
                setSelectedBatchId(e.target.value);
                setSelectedHardware("");
              },
              placeholder: "Select a batch"
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Select,
            {
              label: "Hardware Device",
              options: hardwareOptions,
              value: selectedHardware,
              onChange: (e) => setSelectedHardware(e.target.value),
              placeholder: "Select hardware",
              disabled: !selectedBatchId
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Input,
            {
              label: "Command",
              value: command,
              onChange: (e) => setCommand(e.target.value),
              placeholder: "e.g., move, read, write",
              disabled: !selectedHardware
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("label", { className: "block text-sm font-medium mb-1.5", style: { color: "var(--color-text-secondary)" }, children: "Parameters (JSON)" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "textarea",
              {
                className: "w-full px-3 py-2 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent",
                style: { backgroundColor: "var(--color-bg-tertiary)", borderColor: "var(--color-border-default)", color: "var(--color-text-primary)" },
                rows: 4,
                value: params,
                onChange: (e) => setParams(e.target.value),
                placeholder: '{"key": "value"}',
                disabled: !selectedHardware
              }
            )
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs(
            Button,
            {
              variant: "primary",
              className: "w-full",
              onClick: handleExecute,
              isLoading: manualControl2.isPending,
              disabled: !selectedBatchId || !selectedHardware || !command,
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Send, { className: "w-4 h-4 mr-2" }),
                "Execute Command"
              ]
            }
          )
        ] }),
        isBatchDetail(batchDetail) && batchDetail.hardwareStatus && Object.keys(batchDetail.hardwareStatus).length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("h3", { className: "text-lg font-semibold flex items-center gap-2 mb-4", style: { color: "var(--color-text-primary)" }, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Cpu, { className: "w-5 h-5" }),
            "Hardware Status"
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2", children: Object.entries(batchDetail.hardwareStatus).map(([id, status]) => /* @__PURE__ */ jsxRuntimeExports.jsx(
            HardwareStatusRow,
            {
              id,
              status,
              isSelected: selectedHardware === id
            },
            id
          )) })
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
        lastResult && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-semibold mb-3", style: { color: "var(--color-text-primary)" }, children: "Last Result" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "p-3 rounded font-mono text-sm overflow-x-auto", style: { backgroundColor: "var(--color-bg-tertiary)", color: "var(--color-text-secondary)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsx("pre", { children: JSON.stringify(lastResult.result, null, 2) }) })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("h3", { className: "text-lg font-semibold flex items-center gap-2 mb-4", style: { color: "var(--color-text-primary)" }, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(History, { className: "w-5 h-5" }),
            "Command History"
          ] }),
          commandHistory.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: "No commands executed yet" }) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2 max-h-96 overflow-y-auto", children: commandHistory.map((item) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "div",
            {
              className: "p-3 rounded-lg text-sm",
              style: { backgroundColor: item.success ? "var(--color-bg-tertiary)" : "rgba(239, 68, 68, 0.1)" },
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "font-mono", style: { color: "var(--color-text-primary)" }, children: [
                      item.hardware,
                      ".",
                      item.command
                    ] }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx(
                      StatusBadge,
                      {
                        status: item.success ? "pass" : "fail",
                        size: "sm"
                      }
                    )
                  ] }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: item.timestamp.toLocaleTimeString() })
                ] }),
                Object.keys(item.params).length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-1 text-xs font-mono", style: { color: "var(--color-text-secondary)" }, children: [
                  "Params: ",
                  JSON.stringify(item.params)
                ] })
              ]
            },
            item.id
          )) })
        ] })
      ] })
    ] })
  ] });
}
function HardwareStatusRow({ id, status, isSelected }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "flex items-center justify-between p-2 rounded",
      style: {
        backgroundColor: isSelected ? "rgba(var(--color-brand-rgb), 0.1)" : "var(--color-bg-tertiary)",
        border: isSelected ? "1px solid rgba(var(--color-brand-rgb), 0.3)" : "none"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: id }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "ml-2 text-xs", style: { color: "var(--color-text-tertiary)" }, children: status.driver })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          StatusBadge,
          {
            status: status.status === "connected" ? "connected" : "disconnected",
            size: "sm"
          }
        )
      ]
    }
  );
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
  const levelOptions = [
    { value: "", label: "All Levels" },
    { value: "debug", label: "Debug" },
    { value: "info", label: "Info" },
    { value: "warning", label: "Warning" },
    { value: "error", label: "Error" }
  ];
  const filteredRealTimeLogs = realTimeLogs.filter((log) => {
    if (batchFilter && log.batchId !== batchFilter) return false;
    if (levelFilter && log.level !== levelFilter) return false;
    if (searchFilter && !log.message.toLowerCase().includes(searchFilter.toLowerCase()))
      return false;
    return true;
  });
  const displayLogs = showHistorical ? (historicalLogs == null ? void 0 : historicalLogs.items) ?? [] : filteredRealTimeLogs;
  const handleExport = () => {
    const logs = displayLogs;
    const data = logs.map((log) => ({
      timestamp: new Date(log.timestamp).toISOString(),
      batchId: log.batchId,
      level: log.level,
      message: log.message
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
            options: levelOptions,
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
          children: historicalLoading ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-center h-full", children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "lg" }) }) : displayLogs.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-center h-full", style: { color: "var(--color-text-tertiary)" }, children: showHistorical ? "No logs found" : "No logs yet. Waiting for activity..." }) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "p-2", children: displayLogs.map((log, index) => /* @__PURE__ */ jsxRuntimeExports.jsx(LogEntryRow, { log, showBatchId: true }, log.id ?? index)) })
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
  const updateStationInfo2 = useUpdateStationInfo();
  const addNotification = useNotificationStore((state) => state.addNotification);
  const theme = useUIStore((state) => state.theme);
  const toggleTheme = useUIStore((state) => state.toggleTheme);
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  const lastHeartbeat = useConnectionStore((state) => state.lastHeartbeat);
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
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Section,
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
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow, { label: "Station ID", value: systemInfo.stationId }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow, { label: "Station Name", value: systemInfo.stationName }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow, { label: "Description", value: systemInfo.description || "-" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow, { label: "Version", value: systemInfo.version }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow, { label: "Uptime", value: formatUptime(systemInfo.uptime) })
          ] }) })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Section,
        {
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Monitor, { className: "w-5 h-5" }),
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
      /* @__PURE__ */ jsxRuntimeExports.jsx(Section, { icon: theme === "dark" ? /* @__PURE__ */ jsxRuntimeExports.jsx(Moon, { className: "w-5 h-5" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Sun, { className: "w-5 h-5" }), title: "Appearance", children: /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-4", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: "Theme" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-1", style: { color: "var(--color-text-tertiary)" }, children: "Switch between dark and light mode" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Button,
          {
            variant: "secondary",
            size: "sm",
            onClick: toggleTheme,
            children: theme === "dark" ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Sun, { className: "w-4 h-4 mr-2" }),
              "Light"
            ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Moon, { className: "w-4 h-4 mr-2" }),
              "Dark"
            ] })
          }
        )
      ] }) }) })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "p-4 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between text-sm", style: { color: "var(--color-text-tertiary)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
        "Station Service v",
        (systemInfo == null ? void 0 : systemInfo.version) ?? "..."
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
        "WebSocket: ",
        websocketStatus,
        " | Backend:",
        " ",
        (health == null ? void 0 : health.backendStatus) ?? "unknown"
      ] })
    ] }) })
  ] });
}
function Section({ icon, title, children, isLoading, action }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("h3", { className: "flex items-center gap-2 text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: [
        icon,
        title
      ] }),
      action
    ] }),
    isLoading ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "py-8 flex items-center justify-center", children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, {}) }) : children
  ] });
}
function InfoRow({ label, value }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: label }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: value })
  ] });
}
function EditableRow({ label, value, onChange, placeholder }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between gap-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("label", { className: "text-sm whitespace-nowrap", style: { color: "var(--color-text-secondary)" }, children: label }),
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
function AppContent() {
  usePollingFallback();
  const theme = useUIStore((state) => state.theme);
  reactExports.useEffect(() => {
    document.documentElement.classList.remove("dark", "light");
    document.documentElement.classList.add(theme);
  }, [theme]);
  return /* @__PURE__ */ jsxRuntimeExports.jsx(Layout, { children: /* @__PURE__ */ jsxRuntimeExports.jsxs(Routes, { children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.DASHBOARD, element: /* @__PURE__ */ jsxRuntimeExports.jsx(DashboardPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.BATCHES, element: /* @__PURE__ */ jsxRuntimeExports.jsx(BatchesPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.BATCH_DETAIL, element: /* @__PURE__ */ jsxRuntimeExports.jsx(BatchDetailPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.SEQUENCES, element: /* @__PURE__ */ jsxRuntimeExports.jsx(SequencesPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.SEQUENCE_DETAIL, element: /* @__PURE__ */ jsxRuntimeExports.jsx(SequencesPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.MANUAL, element: /* @__PURE__ */ jsxRuntimeExports.jsx(ManualControlPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.LOGS, element: /* @__PURE__ */ jsxRuntimeExports.jsx(LogsPage, {}) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.SETTINGS, element: /* @__PURE__ */ jsxRuntimeExports.jsx(SettingsPage, {}) })
  ] }) });
}
function App() {
  return /* @__PURE__ */ jsxRuntimeExports.jsx(AppContent, {});
}
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
    console.error("ErrorBoundary caught an error:", error, errorInfo);
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
clientExports.createRoot(document.getElementById("root")).render(
  /* @__PURE__ */ jsxRuntimeExports.jsx(reactExports.StrictMode, { children: /* @__PURE__ */ jsxRuntimeExports.jsx(ErrorBoundary, { children: /* @__PURE__ */ jsxRuntimeExports.jsx(QueryClientProvider, { client: queryClient, children: /* @__PURE__ */ jsxRuntimeExports.jsx(WebSocketProvider, { children: /* @__PURE__ */ jsxRuntimeExports.jsx(BrowserRouter, { basename: "/ui", children: /* @__PURE__ */ jsxRuntimeExports.jsx(App, {}) }) }) }) }) })
);
