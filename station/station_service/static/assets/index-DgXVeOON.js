var __defProp = Object.defineProperty;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __publicField = (obj, key, value) => __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);
import { j as jsxRuntimeExports, M as MutationCache, Q as QueryClient, u as useQuery, a as useQueryClient, b as useMutation, c as QueryClientProvider } from "./query-CyZJxPQm.js";
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
const Calendar = createLucideIcon("Calendar", [
  ["path", { d: "M8 2v4", key: "1cmpym" }],
  ["path", { d: "M16 2v4", key: "4m81vk" }],
  ["rect", { width: "18", height: "18", x: "3", y: "4", rx: "2", key: "1hopcy" }],
  ["path", { d: "M3 10h18", key: "8toen8" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ChartNoAxesColumn = createLucideIcon("ChartNoAxesColumn", [
  ["line", { x1: "18", x2: "18", y1: "20", y2: "10", key: "1xfpm4" }],
  ["line", { x1: "12", x2: "12", y1: "20", y2: "4", key: "be30l9" }],
  ["line", { x1: "6", x2: "6", y1: "20", y2: "14", key: "1r4le6" }]
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
const CircleArrowUp = createLucideIcon("CircleArrowUp", [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["path", { d: "m16 12-4-4-4 4", key: "177agl" }],
  ["path", { d: "M12 16V8", key: "1sbj14" }]
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
const CircleDot = createLucideIcon("CircleDot", [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["circle", { cx: "12", cy: "12", r: "1", key: "41hilf" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const CirclePlay = createLucideIcon("CirclePlay", [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["polygon", { points: "10 8 16 12 10 16 10 8", key: "1cimsy" }]
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
const ClipboardList = createLucideIcon("ClipboardList", [
  ["rect", { width: "8", height: "4", x: "8", y: "2", rx: "1", ry: "1", key: "tgr4d6" }],
  [
    "path",
    {
      d: "M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2",
      key: "116196"
    }
  ],
  ["path", { d: "M12 11h4", key: "1jrz19" }],
  ["path", { d: "M12 16h4", key: "n85exb" }],
  ["path", { d: "M8 11h.01", key: "1dfujw" }],
  ["path", { d: "M8 16h.01", key: "18s6g9" }]
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
const CloudDownload = createLucideIcon("CloudDownload", [
  ["path", { d: "M12 13v8l-4-4", key: "1f5nwf" }],
  ["path", { d: "m12 21 4-4", key: "1lfcce" }],
  ["path", { d: "M4.393 15.269A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.436 8.284", key: "ui1hmy" }]
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
const FileSpreadsheet = createLucideIcon("FileSpreadsheet", [
  ["path", { d: "M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z", key: "1rqfz7" }],
  ["path", { d: "M14 2v4a2 2 0 0 0 2 2h4", key: "tnqrlb" }],
  ["path", { d: "M8 13h2", key: "yr2amv" }],
  ["path", { d: "M14 13h2", key: "un5t4a" }],
  ["path", { d: "M8 17h2", key: "2yhykz" }],
  ["path", { d: "M14 17h2", key: "10kma7" }]
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
const FlaskConical = createLucideIcon("FlaskConical", [
  [
    "path",
    {
      d: "M14 2v6a2 2 0 0 0 .245.96l5.51 10.08A2 2 0 0 1 18 22H6a2 2 0 0 1-1.755-2.96l5.51-10.08A2 2 0 0 0 10 8V2",
      key: "18mbvz"
    }
  ],
  ["path", { d: "M6.453 15h11.094", key: "3shlmq" }],
  ["path", { d: "M8.5 2h7", key: "csnxdl" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const FolderOpen = createLucideIcon("FolderOpen", [
  [
    "path",
    {
      d: "m6 14 1.5-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.54 6a2 2 0 0 1-1.95 1.5H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H18a2 2 0 0 1 2 2v2",
      key: "usdka0"
    }
  ]
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
const List = createLucideIcon("List", [
  ["path", { d: "M3 12h.01", key: "nlz23k" }],
  ["path", { d: "M3 18h.01", key: "1tta3j" }],
  ["path", { d: "M3 6h.01", key: "1rqtza" }],
  ["path", { d: "M8 12h13", key: "1za7za" }],
  ["path", { d: "M8 18h13", key: "1lx6n3" }],
  ["path", { d: "M8 6h13", key: "ik3vkj" }]
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
const Plug = createLucideIcon("Plug", [
  ["path", { d: "M12 22v-5", key: "1ega77" }],
  ["path", { d: "M9 8V2", key: "14iosj" }],
  ["path", { d: "M15 8V2", key: "18g5xt" }],
  ["path", { d: "M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8Z", key: "osxo6l" }]
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
const Terminal = createLucideIcon("Terminal", [
  ["polyline", { points: "4 17 10 11 4 5", key: "akl6gq" }],
  ["line", { x1: "12", x2: "20", y1: "19", y2: "19", key: "q2wloq" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ToggleLeft = createLucideIcon("ToggleLeft", [
  ["rect", { width: "20", height: "12", x: "2", y: "6", rx: "6", ry: "6", key: "f2vt7d" }],
  ["circle", { cx: "8", cy: "12", r: "2", key: "1nvbw3" }]
]);
/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ToggleRight = createLucideIcon("ToggleRight", [
  ["rect", { width: "20", height: "12", x: "2", y: "6", rx: "6", ry: "6", key: "f2vt7d" }],
  ["circle", { cx: "16", cy: "12", r: "2", key: "4ma0v8" }]
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
const TrendingDown = createLucideIcon("TrendingDown", [
  ["polyline", { points: "22 17 13.5 8.5 8.5 13.5 2 7", key: "1r2t7k" }],
  ["polyline", { points: "16 17 22 17 22 11", key: "11uiuu" }]
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
  RESULTS: "/results",
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
      { path: ROUTES.MANUAL, label: "Manual Control", icon: Wrench },
      { path: ROUTES.RESULTS, label: "Results", icon: ClipboardList }
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
  if (error && typeof error === "object") {
    const err = error;
    if ("detail" in err && typeof err.detail === "string") {
      return err.detail;
    }
    if ("response" in err && err.response && typeof err.response === "object") {
      const response = err.response;
      if ("data" in response && response.data && typeof response.data === "object") {
        const data = response.data;
        if ("detail" in data && typeof data.detail === "string") {
          return data.detail;
        }
        if ("message" in data && typeof data.message === "string") {
          return data.message;
        }
      }
    }
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
          const lastRunPassed = existing.lastRunPassed !== void 0 ? existing.lastRunPassed : batch.lastRunPassed;
          newBatches.set(batch.id, {
            ...batch,
            steps: apiSteps.length > 0 ? apiSteps : existingSteps,
            lastRunPassed
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
    if (batch) {
      const currentStatus = batch.status;
      if (currentStatus === "completed" && status === "idle") {
        batchLogger.batch(batchId, "updateBatchStatus: BLOCKED completed→idle regression (preserving lastRunPassed)", { force: !!force });
        return state;
      }
      if (!force) {
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
  startStep: (batchId, stepName, stepIndex, totalSteps, executionId, stepNames) => set((state) => {
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
    const updatedStepNames = stepNames || batch.stepNames;
    newBatches.set(batchId, {
      ...batch,
      currentStep: stepName,
      stepIndex,
      totalSteps,
      steps: newSteps,
      stepNames: updatedStepNames,
      executionId: executionId || batch.executionId
    });
    batchLogger.batch(batchId, "startStep", { step: stepName, index: stepIndex, hasStepNames: !!stepNames });
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
const ERROR_MESSAGES = {
  UNAUTHORIZED: "API 키가 만료되었거나 유효하지 않습니다. 다시 로그인해주세요.",
  NETWORK_ERROR: "네트워크 연결을 확인해주세요.",
  NOT_FOUND: "요청한 리소스를 찾을 수 없습니다.",
  TIMEOUT: "요청 시간이 초과되었습니다.",
  INTERNAL_ERROR: "서버 내부 오류가 발생했습니다."
};
function extractErrorCode(error) {
  var _a, _b, _c, _d;
  if (!error || typeof error !== "object") return null;
  const axiosError = error;
  if ((_c = (_b = (_a = axiosError.response) == null ? void 0 : _a.data) == null ? void 0 : _b.error) == null ? void 0 : _c.code) {
    return axiosError.response.data.error.code;
  }
  const status = (_d = axiosError.response) == null ? void 0 : _d.status;
  if (status === 401) return "UNAUTHORIZED";
  if (status === 404) return "NOT_FOUND";
  if (status === 500) return "INTERNAL_ERROR";
  const errWithCode = error;
  if (errWithCode.code === "ERR_NETWORK") return "NETWORK_ERROR";
  if (errWithCode.code === "ECONNABORTED") return "TIMEOUT";
  return null;
}
function globalMutationErrorHandler(error) {
  const errorCode = extractErrorCode(error);
  const message = errorCode && ERROR_MESSAGES[errorCode] ? ERROR_MESSAGES[errorCode] : getErrorMessage(error);
  toast.error(message);
  console.error("[API Error]", { errorCode, message, error });
}
const mutationCache = new MutationCache({
  onError: (error, _variables, _context, mutation) => {
    if (mutation.options.onError) return;
    globalMutationErrorHandler(error);
  }
});
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
  defaultOptions: defaultQueryOptions,
  mutationCache
});
const queryKeys = {
  // System
  systemInfo: ["system", "info"],
  healthStatus: ["system", "health"],
  workflowConfig: ["system", "workflow"],
  operatorSession: ["system", "operator"],
  backendConfig: ["system", "backend-config"],
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
async function getBackendConfig() {
  const response = await apiClient.get("/system/backend-config");
  return extractData(response);
}
async function updateBackendConfig(data) {
  const snakeCaseData = {};
  if (data.url !== void 0) snakeCaseData.url = data.url;
  if (data.syncInterval !== void 0) snakeCaseData.sync_interval = data.syncInterval;
  if (data.stationId !== void 0) snakeCaseData.station_id = data.stationId;
  if (data.timeout !== void 0) snakeCaseData.timeout = data.timeout;
  if (data.maxRetries !== void 0) snakeCaseData.max_retries = data.maxRetries;
  const response = await apiClient.put("/system/backend-config", snakeCaseData);
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
      toast.success("스테이션 정보 업데이트 완료");
    }
  });
}
function useBackendConfig() {
  return useQuery({
    queryKey: queryKeys.backendConfig,
    queryFn: getBackendConfig,
    staleTime: POLLING_INTERVALS.systemInfo
  });
}
function useUpdateBackendConfig() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (data) => updateBackendConfig(data),
    onSuccess: (data) => {
      queryClient2.setQueryData(queryKeys.backendConfig, data);
      toast.success("백엔드 설정 업데이트 완료");
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
  var _a, _b, _c, _d, _e, _f, _g, _h, _i, _j;
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
  const stepNames = ((_b = data.execution) == null ? void 0 : _b.stepNames) || steps.map((step) => step.name);
  return {
    id: data.id,
    name: data.name,
    status: data.status,
    sequenceName: ((_c = data.sequence) == null ? void 0 : _c.name) || "",
    sequenceVersion: ((_d = data.sequence) == null ? void 0 : _d.version) || "",
    sequencePackage: ((_e = data.sequence) == null ? void 0 : _e.packagePath) || "",
    currentStep: (_f = data.execution) == null ? void 0 : _f.currentStep,
    stepIndex: ((_g = data.execution) == null ? void 0 : _g.stepIndex) || 0,
    // Prefer stepNames length (from manifest) for accurate total, fall back to API totalSteps or executed steps
    totalSteps: stepNames.length || ((_h = data.execution) == null ? void 0 : _h.totalSteps) || steps.length,
    stepNames,
    progress: ((_i = data.execution) == null ? void 0 : _i.progress) || 0,
    startedAt: void 0,
    elapsed: ((_j = data.execution) == null ? void 0 : _j.elapsed) || 0,
    hardwareConfig: {},
    autoStart: false,
    parameters: data.parameters || {},
    config: data.config || {},
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
async function createBatches(request) {
  const batchIds = [];
  const timestamp = (/* @__PURE__ */ new Date()).toISOString();
  for (let i = 0; i < request.quantity; i++) {
    const batchId = `batch-${Date.now()}-${Math.random().toString(36).substring(2, 9)}-${i}`;
    const batchName = request.quantity > 1 ? `${request.sequenceName} #${i + 1}` : request.sequenceName;
    const serverRequest = {
      id: batchId,
      name: batchName,
      sequence_package: `sequences/${request.sequenceName}`,
      hardware: {},
      auto_start: false,
      parameters: request.parameters,
      process_id: request.processId
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
  if (request.config !== void 0) serverRequest.config = request.config;
  if (request.parameters !== void 0) serverRequest.parameters = request.parameters;
  if (request.processId !== void 0) serverRequest.process_id = request.processId;
  if (request.headerId !== void 0) serverRequest.header_id = request.headerId;
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
async function getSequences() {
  const registry = await getSequenceRegistry();
  return registry.items.filter((item) => ["installed_latest", "update_available", "local_only"].includes(item.status)).map((item) => ({
    name: item.name,
    version: item.localVersion || "0.0.0",
    displayName: item.displayName || item.name,
    description: item.description || "",
    path: `sequences/${item.name}`
  }));
}
async function getSequence(name) {
  const response = await apiClient.get(`/sequences/${name}`);
  return extractData(response);
}
async function deleteSequence(name) {
  await apiClient.delete(`/deploy/local/${name}`);
}
async function downloadSequence(name) {
  const response = await apiClient.get(`/sequences/${name}/download`, {
    responseType: "blob"
  });
  return response.data;
}
async function getSequenceRegistry() {
  const response = await apiClient.get("/deploy/registry");
  const rawData = extractData(response);
  const warnings = response.data.warnings;
  const items = rawData.map((item) => ({
    name: item.name,
    displayName: item.display_name,
    description: item.description,
    status: item.status,
    localVersion: item.local_version,
    remoteVersion: item.remote_version,
    installedAt: item.installed_at,
    remoteUpdatedAt: item.remote_updated_at,
    isActive: item.is_active
  }));
  return { items, warnings };
}
async function pullSequence(name, force = false) {
  const response = await apiClient.post(
    `/deploy/pull/${name}`,
    { force }
  );
  return extractData(response);
}
async function syncSequences(sequenceNames) {
  const response = await apiClient.post("/deploy/sync", { sequence_names: sequenceNames });
  const data = extractData(response);
  return {
    syncedAt: data.synced_at,
    sequencesChecked: data.sequences_checked,
    sequencesUpdated: data.sequences_updated,
    sequencesFailed: data.sequences_failed
  };
}
async function runSimulation(sequenceName, mode, parameters) {
  const response = await apiClient.post(
    `/deploy/simulate/${sequenceName}`,
    { mode, parameters }
  );
  return extractData(response);
}
async function getAutoSyncStatus() {
  const response = await apiClient.get("/deploy/auto-sync/status");
  const data = extractData(response);
  return {
    enabled: data.enabled,
    running: data.running,
    pollInterval: data.poll_interval,
    autoPull: data.auto_pull,
    lastCheckAt: data.last_check_at,
    lastSyncAt: data.last_sync_at,
    updatesAvailable: data.updates_available,
    lastError: data.last_error
  };
}
async function configureAutoSync(config) {
  const response = await apiClient.post("/deploy/auto-sync/configure", config);
  const data = extractData(response);
  return {
    enabled: data.enabled,
    running: data.running,
    pollInterval: data.poll_interval,
    autoPull: data.auto_pull,
    lastCheckAt: data.last_check_at,
    lastSyncAt: data.last_sync_at,
    updatesAvailable: data.updates_available,
    lastError: data.last_error
  };
}
function useSequenceList() {
  return useQuery({
    queryKey: queryKeys.sequences,
    queryFn: getSequences,
    staleTime: 5 * 60 * 1e3
    // 5 minutes
  });
}
function useSequence(name) {
  return useQuery({
    queryKey: queryKeys.sequence(name ?? ""),
    queryFn: () => getSequence(name),
    enabled: !!name
  });
}
function useDeleteSequence() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (name) => deleteSequence(name),
    onSuccess: () => {
      queryClient2.invalidateQueries({ queryKey: queryKeys.sequences });
      queryClient2.invalidateQueries({ queryKey: ["registry"] });
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
function useSequenceRegistry() {
  return useQuery({
    queryKey: ["registry"],
    queryFn: getSequenceRegistry,
    staleTime: 30 * 1e3,
    // 30 seconds
    refetchOnWindowFocus: true
  });
}
function usePullSequence() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: ({ name, force = false }) => pullSequence(name, force),
    onSuccess: async () => {
      await queryClient2.refetchQueries({ queryKey: queryKeys.sequences });
      await queryClient2.refetchQueries({ queryKey: ["registry"] });
    }
  });
}
function useSyncSequences() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (sequenceNames) => syncSequences(sequenceNames),
    onSuccess: async () => {
      await queryClient2.refetchQueries({ queryKey: queryKeys.sequences });
      await queryClient2.refetchQueries({ queryKey: ["registry"] });
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
function useAutoSyncStatus() {
  return useQuery({
    queryKey: ["auto-sync", "status"],
    queryFn: getAutoSyncStatus,
    staleTime: 10 * 1e3,
    // 10 seconds
    refetchInterval: 30 * 1e3
    // Refetch every 30 seconds
  });
}
function useConfigureAutoSync() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (config) => configureAutoSync(config),
    onSuccess: () => {
      queryClient2.invalidateQueries({ queryKey: ["auto-sync"] });
    }
  });
}
async function getResults(params) {
  const response = await apiClient.get("/results", {
    params
  });
  return response.data.data;
}
async function getResult(resultId) {
  const response = await apiClient.get(`/results/${resultId}`);
  return extractData(response);
}
function useResultList(params) {
  return useQuery({
    queryKey: queryKeys.results(params),
    queryFn: () => getResults(params)
  });
}
function useResult(resultId) {
  return useQuery({
    queryKey: queryKeys.result(resultId ?? ""),
    queryFn: () => getResult(resultId),
    enabled: !!resultId
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
          wsLogger.debug(`batch_status: status=${message.data.status}, step=${message.data.currentStep}, progress=${message.data.progress}, exec=${message.data.executionId}, lastRunPassed=${message.data.lastRunPassed}, initial=${isInitialPush}`);
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
          if (isInitialPush && message.data.lastRunPassed !== void 0 && message.data.lastRunPassed !== null) {
            setLastRunResult(message.batchId, message.data.lastRunPassed);
          }
          break;
        }
        case "step_start": {
          wsLogger.debug(`step_start: step=${message.data.step}, index=${message.data.index}/${message.data.total}, exec=${message.data.executionId}, hasStepNames=${!!message.data.stepNames}`);
          startStep(
            message.batchId,
            message.data.step,
            message.data.index,
            message.data.total,
            message.data.executionId,
            message.data.stepNames
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
const MAX_HISTORY_SIZE = 50;
function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
}
create((set) => ({
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
async function createSimulationSession(sequenceName, parameters, hardwareConfig) {
  const response = await apiClient.post(
    "/simulation/sessions",
    {
      sequence_name: sequenceName,
      parameters,
      hardware_config: hardwareConfig
    }
  );
  return extractData(response);
}
async function getSimulationSession(sessionId) {
  const response = await apiClient.get(
    `/simulation/sessions/${sessionId}`
  );
  return extractData(response);
}
async function deleteSimulationSession(sessionId) {
  const response = await apiClient.delete(
    `/simulation/sessions/${sessionId}`
  );
  return extractData(response);
}
async function initializeSimulationSession(sessionId) {
  const response = await apiClient.post(
    `/simulation/sessions/${sessionId}/initialize`
  );
  return extractData(response);
}
async function finalizeSimulationSession(sessionId) {
  const response = await apiClient.post(
    `/simulation/sessions/${sessionId}/finalize`
  );
  return extractData(response);
}
async function abortSimulationSession(sessionId) {
  const response = await apiClient.post(
    `/simulation/sessions/${sessionId}/abort`
  );
  return extractData(response);
}
async function runSimulationStep(sessionId, stepName, parameterOverrides) {
  const response = await apiClient.post(
    `/simulation/sessions/${sessionId}/steps/${stepName}/run`,
    parameterOverrides ? { parameter_overrides: parameterOverrides } : void 0
  );
  return extractData(response);
}
async function skipSimulationStep(sessionId, stepName) {
  const response = await apiClient.post(
    `/simulation/sessions/${sessionId}/steps/${stepName}/skip`
  );
  return extractData(response);
}
const simulationQueryKeys = {
  all: ["simulation"],
  sessions: () => [...simulationQueryKeys.all, "sessions"],
  session: (id) => [...simulationQueryKeys.sessions(), id]
};
function useSimulationSession(sessionId) {
  return useQuery({
    queryKey: simulationQueryKeys.session(sessionId ?? ""),
    queryFn: () => getSimulationSession(sessionId),
    enabled: !!sessionId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data && ["running", "ready"].includes(data.status)) {
        return 1e3;
      }
      return false;
    }
  });
}
function useCreateSimulationSession() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: ({
      sequenceName,
      parameters,
      hardwareConfig
    }) => createSimulationSession(sequenceName, parameters, hardwareConfig),
    onSuccess: () => {
      queryClient2.invalidateQueries({ queryKey: simulationQueryKeys.sessions() });
    }
  });
}
function useDeleteSimulationSession() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (sessionId) => deleteSimulationSession(sessionId),
    onSuccess: () => {
      queryClient2.invalidateQueries({ queryKey: simulationQueryKeys.sessions() });
    }
  });
}
function useInitializeSimulationSession() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (sessionId) => initializeSimulationSession(sessionId),
    onSuccess: (data) => {
      queryClient2.setQueryData(simulationQueryKeys.session(data.id), data);
    }
  });
}
function useFinalizeSimulationSession() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (sessionId) => finalizeSimulationSession(sessionId),
    onSuccess: (data) => {
      queryClient2.setQueryData(simulationQueryKeys.session(data.id), data);
    }
  });
}
function useAbortSimulationSession() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (sessionId) => abortSimulationSession(sessionId),
    onSuccess: (data) => {
      queryClient2.setQueryData(simulationQueryKeys.session(data.id), data);
    }
  });
}
function useRunSimulationStep() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      stepName,
      parameterOverrides
    }) => runSimulationStep(sessionId, stepName, parameterOverrides),
    onSuccess: (data, variables) => {
      queryClient2.setQueryData(
        simulationQueryKeys.session(variables.sessionId),
        (old) => {
          if (!old) return old;
          return {
            ...old,
            steps: old.steps.map((s) => s.name === data.name ? data : s)
          };
        }
      );
      queryClient2.invalidateQueries({
        queryKey: simulationQueryKeys.session(variables.sessionId)
      });
    }
  });
}
function useSkipSimulationStep() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      stepName
    }) => skipSimulationStep(sessionId, stepName),
    onSuccess: (data, variables) => {
      queryClient2.setQueryData(
        simulationQueryKeys.session(variables.sessionId),
        (old) => {
          if (!old) return old;
          return {
            ...old,
            steps: old.steps.map((s) => s.name === data.name ? data : s)
          };
        }
      );
      queryClient2.invalidateQueries({
        queryKey: simulationQueryKeys.session(variables.sessionId)
      });
    }
  });
}
async function createManualSession(sequenceName, hardwareConfig, parameters) {
  const response = await apiClient.post(
    "/manual-sequence/sessions",
    {
      sequence_name: sequenceName,
      hardware_config: hardwareConfig,
      parameters
    }
  );
  return extractData(response);
}
async function getManualSession(sessionId) {
  const response = await apiClient.get(
    `/manual-sequence/sessions/${sessionId}`
  );
  return extractData(response);
}
async function deleteManualSession(sessionId) {
  const response = await apiClient.delete(
    `/manual-sequence/sessions/${sessionId}`
  );
  return extractData(response);
}
async function initializeManualSession(sessionId) {
  const response = await apiClient.post(
    `/manual-sequence/sessions/${sessionId}/initialize`
  );
  return extractData(response);
}
async function finalizeManualSession(sessionId) {
  const response = await apiClient.post(
    `/manual-sequence/sessions/${sessionId}/finalize`
  );
  return extractData(response);
}
async function abortManualSession(sessionId) {
  const response = await apiClient.post(
    `/manual-sequence/sessions/${sessionId}/abort`
  );
  return extractData(response);
}
async function runManualStep(sessionId, stepName, parameterOverrides) {
  const response = await apiClient.post(
    `/manual-sequence/sessions/${sessionId}/steps/${stepName}/run`,
    parameterOverrides ? { parameter_overrides: parameterOverrides } : void 0
  );
  return extractData(response);
}
async function skipManualStep(sessionId, stepName) {
  const response = await apiClient.post(
    `/manual-sequence/sessions/${sessionId}/steps/${stepName}/skip`
  );
  return extractData(response);
}
const manualSequenceQueryKeys = {
  all: ["manual-sequence"],
  sessions: () => [...manualSequenceQueryKeys.all, "sessions"],
  session: (id) => [...manualSequenceQueryKeys.sessions(), id],
  hardware: (sessionId) => [...manualSequenceQueryKeys.session(sessionId), "hardware"],
  commands: (sessionId, hardwareId) => [...manualSequenceQueryKeys.hardware(sessionId), hardwareId, "commands"]
};
function useManualSession(sessionId) {
  return useQuery({
    queryKey: manualSequenceQueryKeys.session(sessionId ?? ""),
    queryFn: () => getManualSession(sessionId),
    enabled: !!sessionId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data && ["connecting", "running", "ready"].includes(data.status)) {
        return 1e3;
      }
      return false;
    }
  });
}
function useCreateManualSession() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: ({
      sequenceName,
      hardwareConfig,
      parameters
    }) => createManualSession(sequenceName, hardwareConfig, parameters),
    onSuccess: () => {
      queryClient2.invalidateQueries({ queryKey: manualSequenceQueryKeys.sessions() });
    }
  });
}
function useDeleteManualSession() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (sessionId) => deleteManualSession(sessionId),
    onSuccess: () => {
      queryClient2.invalidateQueries({ queryKey: manualSequenceQueryKeys.sessions() });
    }
  });
}
function useInitializeManualSession() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (sessionId) => initializeManualSession(sessionId),
    onSuccess: (data) => {
      queryClient2.setQueryData(manualSequenceQueryKeys.session(data.id), data);
    }
  });
}
function useFinalizeManualSession() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (sessionId) => finalizeManualSession(sessionId),
    onSuccess: (data) => {
      queryClient2.setQueryData(manualSequenceQueryKeys.session(data.id), data);
    }
  });
}
function useAbortManualSession() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: (sessionId) => abortManualSession(sessionId),
    onSuccess: (data) => {
      queryClient2.setQueryData(manualSequenceQueryKeys.session(data.id), data);
    }
  });
}
function useRunManualStep() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      stepName,
      parameterOverrides
    }) => runManualStep(sessionId, stepName, parameterOverrides),
    onSuccess: (data, variables) => {
      queryClient2.setQueryData(
        manualSequenceQueryKeys.session(variables.sessionId),
        (old) => {
          if (!old) return old;
          return {
            ...old,
            steps: old.steps.map((s) => s.name === data.name ? data : s)
          };
        }
      );
      queryClient2.invalidateQueries({
        queryKey: manualSequenceQueryKeys.session(variables.sessionId)
      });
    }
  });
}
function useSkipManualStep() {
  const queryClient2 = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      stepName
    }) => skipManualStep(sessionId, stepName),
    onSuccess: (data, variables) => {
      queryClient2.setQueryData(
        manualSequenceQueryKeys.session(variables.sessionId),
        (old) => {
          if (!old) return old;
          return {
            ...old,
            steps: old.steps.map((s) => s.name === data.name ? data : s)
          };
        }
      );
      queryClient2.invalidateQueries({
        queryKey: manualSequenceQueryKeys.session(variables.sessionId)
      });
    }
  });
}
async function getBatchSummaryReport(batchId, batchName) {
  const response = await apiClient.get(
    `/reports/batch/${batchId}`,
    { params: { batchName } }
  );
  return extractData(response);
}
async function exportBatchSummaryReport(batchId, format, batchName) {
  const response = await apiClient.get(`/reports/batch/${batchId}`, {
    params: { format, batchName },
    responseType: "blob"
  });
  return response.data;
}
async function getPeriodStatsReport(periodType, fromDate, toDate, batchId) {
  const response = await apiClient.get("/reports/period", {
    params: {
      period: periodType,
      from: fromDate,
      to: toDate,
      batchId
    }
  });
  return extractData(response);
}
async function exportPeriodStatsReport(periodType, fromDate, toDate, format, batchId) {
  const response = await apiClient.get("/reports/period", {
    params: {
      period: periodType,
      from: fromDate,
      to: toDate,
      batchId,
      format
    },
    responseType: "blob"
  });
  return response.data;
}
async function getStepAnalysisReport(filters) {
  const response = await apiClient.get(
    "/reports/step-analysis",
    {
      params: {
        from: filters == null ? void 0 : filters.fromDate,
        to: filters == null ? void 0 : filters.toDate,
        batchId: filters == null ? void 0 : filters.batchId,
        stepName: filters == null ? void 0 : filters.stepName
      }
    }
  );
  return extractData(response);
}
async function exportStepAnalysisReport(format, filters) {
  const response = await apiClient.get("/reports/step-analysis", {
    params: {
      from: filters == null ? void 0 : filters.fromDate,
      to: filters == null ? void 0 : filters.toDate,
      batchId: filters == null ? void 0 : filters.batchId,
      stepName: filters == null ? void 0 : filters.stepName,
      format
    },
    responseType: "blob"
  });
  return response.data;
}
async function exportResultsBulk(request) {
  const response = await apiClient.post("/results/export", request, {
    responseType: "blob"
  });
  return response.data;
}
function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
function getFileExtension(format) {
  return format;
}
const reportQueryKeys = {
  all: ["reports"],
  batchSummary: (batchId) => ["reports", "batch", batchId],
  periodStats: (period, from, to, batchId) => ["reports", "period", period, from, to, batchId],
  stepAnalysis: (filters) => ["reports", "step-analysis", filters],
  types: () => ["reports", "types"]
};
function useBatchSummaryReport(batchId, batchName, options) {
  return useQuery({
    queryKey: reportQueryKeys.batchSummary(batchId ?? ""),
    queryFn: () => getBatchSummaryReport(batchId, batchName),
    enabled: !!batchId,
    ...options
  });
}
function useExportBatchSummaryReport() {
  return useMutation({
    mutationFn: ({
      batchId,
      format,
      batchName
    }) => exportBatchSummaryReport(batchId, format, batchName),
    onSuccess: (blob, { batchId, format }) => {
      const filename = `batch_summary_${batchId}_${(/* @__PURE__ */ new Date()).toISOString().slice(0, 10)}.${getFileExtension(format)}`;
      downloadBlob(blob, filename);
      toast.success("리포트 다운로드 완료");
    }
  });
}
function usePeriodStatsReport(periodType, fromDate, toDate, batchId, options) {
  return useQuery({
    queryKey: reportQueryKeys.periodStats(periodType, fromDate ?? "", toDate ?? "", batchId),
    queryFn: () => getPeriodStatsReport(periodType, fromDate, toDate, batchId),
    enabled: !!fromDate && !!toDate,
    ...options
  });
}
function useExportPeriodStatsReport() {
  return useMutation({
    mutationFn: ({
      periodType,
      fromDate,
      toDate,
      format,
      batchId
    }) => exportPeriodStatsReport(periodType, fromDate, toDate, format, batchId),
    onSuccess: (blob, { periodType, format }) => {
      const filename = `period_stats_${periodType}_${(/* @__PURE__ */ new Date()).toISOString().slice(0, 10)}.${getFileExtension(format)}`;
      downloadBlob(blob, filename);
      toast.success("리포트 다운로드 완료");
    }
  });
}
function useStepAnalysisReport(filters, options) {
  return useQuery({
    queryKey: reportQueryKeys.stepAnalysis(filters),
    queryFn: () => getStepAnalysisReport(filters),
    ...options
  });
}
function useExportStepAnalysisReport() {
  return useMutation({
    mutationFn: ({
      format,
      filters
    }) => exportStepAnalysisReport(format, filters),
    onSuccess: (blob, { format }) => {
      const filename = `step_analysis_${(/* @__PURE__ */ new Date()).toISOString().slice(0, 10)}.${getFileExtension(format)}`;
      downloadBlob(blob, filename);
      toast.success("리포트 다운로드 완료");
    }
  });
}
function useExportResultsBulk() {
  return useMutation({
    mutationFn: (request) => exportResultsBulk(request),
    onSuccess: (blob, { format }) => {
      const filename = `results_export_${(/* @__PURE__ */ new Date()).toISOString().slice(0, 10)}.${getFileExtension(format)}`;
      downloadBlob(blob, filename);
      toast.success("결과 내보내기 완료");
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
function StatusBadge$1({ status, size = "md", className = "" }) {
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
                StatusBadge$1,
                {
                  status: isStationServiceConnected ? (health == null ? void 0 : health.status) === "healthy" ? "connected" : "warning" : "disconnected",
                  size: "sm"
                }
              ) })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Backend (MES)" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "mt-1", children: !isStationServiceConnected ? /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge$1, { status: "disconnected", size: "sm" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(
                StatusBadge$1,
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
                  StatusBadge$1,
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
            /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge$1, { status: batch.status, size: "sm" })
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
  const statusOptions2 = [
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
          options: statusOptions2,
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
  const [selectedProcessId, setSelectedProcessId] = reactExports.useState(void 0);
  const { data: workflowConfig } = useWorkflowConfig();
  const { data: processes = [] } = useProcesses();
  const isWorkflowEnabled = (workflowConfig == null ? void 0 : workflowConfig.enabled) ?? false;
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
      setSelectedProcessId(void 0);
    }
  }, [isOpen]);
  const handleSequenceSelect = reactExports.useCallback(
    async (sequenceName) => {
      console.log("[CreateBatchWizard] handleSequenceSelect called with:", sequenceName);
      setSelectedSequence(sequenceName);
      if (!sequenceName) {
        setSequenceDetail(null);
        setStepOrder([]);
        setParameters({});
        return;
      }
      setIsLoadingSequence(true);
      try {
        console.log("[CreateBatchWizard] Fetching sequence detail for:", sequenceName);
        const detail = await getSequenceDetail(sequenceName);
        console.log("[CreateBatchWizard] Received sequence detail:", detail);
        if (!detail) {
          console.error("[CreateBatchWizard] Received null/undefined detail");
          return;
        }
        setSequenceDetail(detail);
        const steps = detail.steps || [];
        console.log("[CreateBatchWizard] Steps count:", steps.length);
        setStepOrder(
          steps.map((step) => ({
            name: step.name,
            displayName: step.displayName,
            order: step.order,
            enabled: true
          }))
        );
        const defaultParams = {};
        const params = detail.parameters || [];
        params.forEach((param) => {
          defaultParams[param.name] = param.default;
        });
        setParameters(defaultParams);
      } catch (error) {
        console.error("[CreateBatchWizard] Failed to load sequence:", error);
        setSequenceDetail(null);
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
      parameters,
      processId: selectedProcessId
    };
    onSubmit(request);
  };
  const canProceed = reactExports.useMemo(() => {
    switch (currentStep) {
      case "sequence": {
        const baseValid = !!selectedSequence && !!sequenceDetail;
        return isWorkflowEnabled ? baseValid && !!selectedProcessId : baseValid;
      }
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
  }, [currentStep, selectedSequence, sequenceDetail, stepOrder, quantity, isWorkflowEnabled, selectedProcessId]);
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
          isLoading: isLoadingSequence,
          isWorkflowEnabled,
          processes,
          selectedProcessId,
          onProcessSelect: setSelectedProcessId
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
          quantity,
          isWorkflowEnabled,
          selectedProcessId,
          processes
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
  isLoading,
  isWorkflowEnabled,
  processes,
  selectedProcessId,
  onProcessSelect
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
    isWorkflowEnabled && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("h3", { className: "text-lg font-medium mb-2", style: { color: "var(--color-text-primary)" }, children: [
        "MES Process ",
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-red-500", children: "*" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mb-4", style: { color: "var(--color-text-secondary)" }, children: "WIP 연동이 활성화되어 있습니다. 이 배치에서 실행할 MES 공정을 선택하세요." }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "select",
        {
          value: selectedProcessId ?? "",
          onChange: (e) => {
            const value = e.target.value;
            onProcessSelect(value ? parseInt(value, 10) : void 0);
          },
          className: "w-full px-3 py-2 rounded-lg border outline-none transition-colors text-sm",
          style: {
            backgroundColor: "var(--color-bg-secondary)",
            borderColor: selectedProcessId ? "var(--color-border-default)" : "var(--color-status-fail)",
            color: "var(--color-text-primary)"
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "", disabled: true, children: "-- Select MES Process --" }),
            processes.map((process2) => /* @__PURE__ */ jsxRuntimeExports.jsxs("option", { value: process2.id, children: [
              process2.processNumber,
              ". ",
              process2.processNameEn
            ] }, process2.id))
          ]
        }
      ),
      !selectedProcessId && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mt-2 text-xs", style: { color: "var(--color-status-fail)" }, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(CircleAlert, { className: "w-3.5 h-3.5" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "MES Process 선택이 필요합니다" })
      ] })
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
  quantity,
  isWorkflowEnabled,
  selectedProcessId,
  processes
}) {
  const enabledSteps = stepOrder.filter((s) => s.enabled);
  const selectedProcess = processes.find((p) => p.id === selectedProcessId);
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
      isWorkflowEnabled && selectedProcess && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 rounded-lg border", style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" }, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "text-sm font-medium mb-2", style: { color: "var(--color-text-secondary)" }, children: "MES Process" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: [
          selectedProcess.processNumber,
          ". ",
          selectedProcess.processNameEn
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
function StepRow$3({ step, isSelected, isExpanded, onToggle, onClick }) {
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
                step.status === "running" && /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge$1, { status: "running", size: "sm" }),
                step.status === "failed" && /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-3.5 h-3.5 text-red-500" }),
                hasData && /* @__PURE__ */ jsxRuntimeExports.jsx("span", { title: "Has data", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Database, { className: "w-3 h-3", style: { color: "var(--color-text-tertiary)" } }) }),
                hasData && /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "button",
                  {
                    onClick: handleCopy,
                    className: "p-1 rounded hover:bg-zinc-700 transition-colors",
                    title: "Copy step data to clipboard",
                    children: copied ? /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "w-3.5 h-3.5 text-green-500" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Copy, { className: "w-3.5 h-3.5", style: { color: "var(--color-text-tertiary)" } })
                  }
                )
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
    StepRow$3,
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
function isBatchDetail$2(batch) {
  return batch !== null && typeof batch === "object" && "config" in batch;
}
function BatchConfigEditor({ batchId, isRunning, onDirtyChange }) {
  const { data: batch } = useBatch(batchId);
  const { data: workflowConfig } = useWorkflowConfig();
  const { data: processes = [] } = useProcesses();
  const updateBatch2 = useUpdateBatch();
  const addNotification = useNotificationStore((state) => state.addNotification);
  const [editedConfig, setEditedConfig] = reactExports.useState({});
  const [originalConfig, setOriginalConfig] = reactExports.useState("");
  const [searchQuery, setSearchQuery] = reactExports.useState("");
  const [saveStatus, setSaveStatus] = reactExports.useState("idle");
  const isWorkflowEnabled = (workflowConfig == null ? void 0 : workflowConfig.enabled) ?? false;
  const processId = editedConfig.processId;
  const headerId = editedConfig.headerId;
  const isMesProcessMissing = isWorkflowEnabled && !processId;
  const isDirty = reactExports.useMemo(() => {
    return JSON.stringify(editedConfig) !== originalConfig;
  }, [editedConfig, originalConfig]);
  reactExports.useEffect(() => {
    onDirtyChange == null ? void 0 : onDirtyChange(isDirty);
  }, [isDirty, onDirtyChange]);
  reactExports.useEffect(() => {
    if (batch && isBatchDetail$2(batch)) {
      const config = { ...batch.config || {} };
      setEditedConfig(config);
      setOriginalConfig(JSON.stringify(config));
      setSaveStatus("idle");
    }
  }, [batch]);
  const filteredConfig = reactExports.useMemo(() => {
    if (!searchQuery.trim()) {
      return Object.entries(editedConfig);
    }
    const query = searchQuery.toLowerCase();
    return Object.entries(editedConfig).filter(
      ([key, value]) => key.toLowerCase().includes(query) || String(value ?? "").toLowerCase().includes(query)
    );
  }, [editedConfig, searchQuery]);
  const handleSave = reactExports.useCallback(async () => {
    if (!batchId || isRunning || !isDirty) return;
    if (isWorkflowEnabled && !editedConfig.processId) {
      addNotification({
        type: "error",
        title: "MES Process Required",
        message: "WIP Process Start/Complete is enabled. Please set processId."
      });
      return;
    }
    setSaveStatus("saving");
    try {
      await updateBatch2.mutateAsync({ batchId, request: { config: editedConfig } });
      setOriginalConfig(JSON.stringify(editedConfig));
      setSaveStatus("saved");
      setTimeout(() => setSaveStatus("idle"), 1500);
    } catch (error) {
      setSaveStatus("idle");
      addNotification({
        type: "error",
        title: "Save Failed",
        message: error instanceof Error ? error.message : "Failed to save configuration"
      });
      console.error("[BatchConfigEditor] Failed to save config:", error);
    }
  }, [batchId, isRunning, isDirty, isWorkflowEnabled, editedConfig, updateBatch2, addNotification]);
  const handleConfigChange = (key, value) => {
    const newConfig = { ...editedConfig };
    if (value === "true") {
      newConfig[key] = true;
    } else if (value === "false") {
      newConfig[key] = false;
    } else if (!isNaN(Number(value)) && value !== "") {
      newConfig[key] = Number(value);
    } else {
      newConfig[key] = value;
    }
    setEditedConfig(newConfig);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col h-full", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "flex items-center justify-between px-3 py-2 border-b shrink-0",
        style: { borderColor: "var(--color-border-default)" },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Settings, { className: "w-4 h-4", style: { color: "var(--color-text-tertiary)" } }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: "Configuration" }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: [
              "(",
              filteredConfig.length,
              "/",
              Object.keys(editedConfig).length,
              ")"
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center gap-1", children: saveStatus === "saved" ? /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1 text-xs px-2 py-1", style: { color: "var(--color-status-pass)" }, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "w-3 h-3" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Saved" })
          ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx(
            "button",
            {
              onClick: handleSave,
              disabled: !isDirty || isRunning || saveStatus === "saving",
              className: "flex items-center gap-1 text-xs px-2 py-1 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
              style: {
                backgroundColor: isDirty && saveStatus !== "saving" ? "var(--color-brand-500)" : "var(--color-bg-tertiary)",
                color: isDirty && saveStatus !== "saving" ? "white" : "var(--color-text-tertiary)"
              },
              title: !isDirty ? "No changes to save" : isRunning ? "Cannot save while running" : "Save changes",
              children: saveStatus === "saving" ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-3 h-3 animate-spin" }),
                /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Saving..." })
              ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Save, { className: "w-3 h-3" }),
                /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Save" })
              ] })
            }
          ) })
        ]
      }
    ),
    Object.keys(editedConfig).length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "px-3 py-2 border-b shrink-0", style: { borderColor: "var(--color-border-default)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative", children: [
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
          placeholder: "Search config...",
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
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "label",
          {
            className: "block text-xs font-medium mb-1.5",
            style: { color: "var(--color-text-secondary)" },
            children: "MES Process"
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "select",
          {
            value: processId ?? "",
            onChange: (e) => handleConfigChange("processId", e.target.value),
            disabled: isRunning,
            className: "w-full text-xs rounded px-2 py-1.5 border outline-none transition-colors disabled:opacity-50",
            style: {
              backgroundColor: "var(--color-bg-tertiary)",
              borderColor: processId ? "var(--color-border-default)" : "var(--color-status-fail)",
              color: "var(--color-text-primary)"
            },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "", disabled: true, children: "-- Select MES Process --" }),
              processes.map((process2) => /* @__PURE__ */ jsxRuntimeExports.jsxs("option", { value: process2.id, children: [
                process2.processNumber,
                ". ",
                process2.processNameEn
              ] }, process2.id))
            ]
          }
        )
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-4 pb-3 border-b", style: { borderColor: "var(--color-border-default)" }, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "label",
          {
            className: "block text-xs font-medium mb-1.5",
            style: { color: "var(--color-text-secondary)" },
            children: "Header ID"
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "input",
          {
            type: "number",
            value: headerId ?? "",
            onChange: (e) => handleConfigChange("headerId", e.target.value),
            disabled: isRunning,
            placeholder: "Enter header ID (e.g., 1, 2, 3...)",
            className: "w-full text-xs rounded px-2 py-1.5 border outline-none transition-colors disabled:opacity-50",
            style: {
              backgroundColor: "var(--color-bg-tertiary)",
              borderColor: headerId ? "var(--color-border-default)" : "var(--color-status-warning)",
              color: "var(--color-text-primary)"
            }
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs mt-1", style: { color: "var(--color-text-tertiary)" }, children: "Unique ID to distinguish batches within the same process" })
      ] }),
      Object.keys(editedConfig).filter((k) => k !== "processId" && k !== "headerId").length === 0 ? !isWorkflowEnabled && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs italic", style: { color: "var(--color-text-tertiary)" }, children: "No configuration for this batch." }) : filteredConfig.filter(([k]) => k !== "processId" && k !== "headerId").length === 0 ? searchQuery && /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs italic", style: { color: "var(--color-text-tertiary)" }, children: [
        'No config matches "',
        searchQuery,
        '"'
      ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2", children: filteredConfig.filter(([key]) => key !== "processId" && key !== "headerId").map(([key, value]) => /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
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
            onChange: (e) => handleConfigChange(key, e.target.value),
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
      isMesProcessMissing && /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "flex items-center gap-2 text-xs p-2 rounded mt-4",
          style: {
            backgroundColor: "rgba(239, 68, 68, 0.1)",
            color: "var(--color-status-fail)"
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-3.5 h-3.5 flex-shrink-0" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "WIP Process Start/Complete is enabled. processId is required." })
          ]
        }
      ),
      isDirty && !isRunning && /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "flex items-center gap-2 text-xs p-2 rounded mt-4",
          style: {
            backgroundColor: "rgba(234, 179, 8, 0.1)",
            color: "var(--color-status-warning)"
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-3.5 h-3.5 flex-shrink-0" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "You have unsaved changes. Click Save to apply." })
          ]
        }
      ),
      isRunning && /* @__PURE__ */ jsxRuntimeExports.jsx(
        "div",
        {
          className: "text-xs p-2 rounded mt-4",
          style: {
            backgroundColor: "rgba(var(--color-brand-rgb), 0.1)",
            color: "var(--color-brand-500)"
          },
          children: "Configuration editing is disabled while the batch is running."
        }
      )
    ] })
  ] });
}
function isBatchDetail$1(batch) {
  return batch !== null && typeof batch === "object" && "parameters" in batch;
}
function ParametersEditor({ batchId, isRunning, onDirtyChange }) {
  const { data: batch } = useBatch(batchId);
  const updateBatch2 = useUpdateBatch();
  const addNotification = useNotificationStore((state) => state.addNotification);
  const [editedParams, setEditedParams] = reactExports.useState({});
  const [originalParams, setOriginalParams] = reactExports.useState("");
  const [searchQuery, setSearchQuery] = reactExports.useState("");
  const [saveStatus, setSaveStatus] = reactExports.useState("idle");
  const isDirty = reactExports.useMemo(() => {
    return JSON.stringify(editedParams) !== originalParams;
  }, [editedParams, originalParams]);
  reactExports.useEffect(() => {
    onDirtyChange == null ? void 0 : onDirtyChange(isDirty);
  }, [isDirty, onDirtyChange]);
  reactExports.useEffect(() => {
    if (batch && isBatchDetail$1(batch)) {
      const params = batch.parameters || {};
      setEditedParams(params);
      setOriginalParams(JSON.stringify(params));
      setSaveStatus("idle");
    }
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
  const handleSave = reactExports.useCallback(async () => {
    if (!batchId || isRunning || !isDirty) return;
    setSaveStatus("saving");
    try {
      await updateBatch2.mutateAsync({ batchId, request: { parameters: editedParams } });
      setOriginalParams(JSON.stringify(editedParams));
      setSaveStatus("saved");
      setTimeout(() => setSaveStatus("idle"), 1500);
    } catch (error) {
      setSaveStatus("idle");
      addNotification({
        type: "error",
        title: "Save Failed",
        message: error instanceof Error ? error.message : "Failed to save parameters"
      });
      console.error("[ParametersEditor] Failed to save params:", error);
    }
  }, [batchId, isRunning, isDirty, editedParams, updateBatch2, addNotification]);
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
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center gap-1", children: saveStatus === "saved" ? /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1 text-xs px-2 py-1", style: { color: "var(--color-status-pass)" }, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "w-3 h-3" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Saved" })
          ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx(
            "button",
            {
              onClick: handleSave,
              disabled: !isDirty || isRunning || saveStatus === "saving",
              className: "flex items-center gap-1 text-xs px-2 py-1 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
              style: {
                backgroundColor: isDirty && saveStatus !== "saving" ? "var(--color-brand-500)" : "var(--color-bg-tertiary)",
                color: isDirty && saveStatus !== "saving" ? "white" : "var(--color-text-tertiary)"
              },
              title: !isDirty ? "No changes to save" : isRunning ? "Cannot save while running" : "Save changes",
              children: saveStatus === "saving" ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-3 h-3 animate-spin" }),
                /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Saving..." })
              ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Save, { className: "w-3 h-3" }),
                /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Save" })
              ] })
            }
          ) })
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
      isDirty && !isRunning && /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "flex items-center gap-2 text-xs p-2 rounded mt-4",
          style: {
            backgroundColor: "rgba(234, 179, 8, 0.1)",
            color: "var(--color-status-warning)"
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-3.5 h-3.5 flex-shrink-0" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "You have unsaved changes. Click Save to apply." })
          ]
        }
      ),
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
function DebugLogPanel({ batchId, steps, isRunning = false, onPendingChangesChange }) {
  const { activeTab, setActiveTab, selectedStep, logLevel, searchQuery } = useDebugPanelStore();
  const logs = useLogStore((s) => s.logs);
  const clearLogs = useLogStore((s) => s.clearLogs);
  const [configDirty, setConfigDirty] = reactExports.useState(false);
  const [paramsDirty, setParamsDirty] = reactExports.useState(false);
  const [copied, setCopied] = reactExports.useState(false);
  const hasPendingChanges = configDirty || paramsDirty;
  reactExports.useEffect(() => {
    onPendingChangesChange == null ? void 0 : onPendingChangesChange(hasPendingChanges);
  }, [hasPendingChanges, onPendingChangesChange]);
  const handleConfigDirtyChange = reactExports.useCallback((isDirty) => {
    setConfigDirty(isDirty);
  }, []);
  const handleParamsDirtyChange = reactExports.useCallback((isDirty) => {
    setParamsDirty(isDirty);
  }, []);
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
  const formatLogsAsText = reactExports.useCallback(() => {
    return filteredLogs.map((log2) => {
      const time = log2.timestamp.toLocaleTimeString("en-US", {
        hour12: false,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
      });
      return `${time} [${log2.level.toUpperCase()}] ${log2.message}`;
    }).join("\n");
  }, [filteredLogs]);
  const handleCopyLogs = reactExports.useCallback(async () => {
    const content = formatLogsAsText();
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2e3);
    } catch (err) {
      console.error("Failed to copy logs:", err);
    }
  }, [formatLogsAsText]);
  const handleExportLogs = () => {
    const content = formatLogsAsText();
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
            activeTab === "logs" && /* @__PURE__ */ jsxRuntimeExports.jsx(
              Button,
              {
                variant: "ghost",
                size: "sm",
                onClick: handleCopyLogs,
                disabled: filteredLogs.length === 0,
                title: copied ? "Copied!" : "Copy logs to clipboard",
                className: "p-1",
                children: copied ? /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "w-3.5 h-3.5 text-green-500" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Copy, { className: "w-3.5 h-3.5" })
              }
            ),
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
      activeTab === "params" && /* @__PURE__ */ jsxRuntimeExports.jsx(
        ParametersEditor,
        {
          batchId,
          isRunning,
          onDirtyChange: handleParamsDirtyChange
        }
      ),
      activeTab === "config" && /* @__PURE__ */ jsxRuntimeExports.jsx(
        BatchConfigEditor,
        {
          batchId,
          isRunning,
          onDirtyChange: handleConfigDirtyChange
        }
      )
    ] })
  ] });
}
const LAST_WIP_ID_KEY = "station-ui-last-wip-id";
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
    if (isOpen) {
      const lastWipId = localStorage.getItem(LAST_WIP_ID_KEY);
      if (lastWipId) {
        setWipId(lastWipId);
      }
      if (inputRef.current) {
        inputRef.current.focus();
        inputRef.current.select();
      }
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
    localStorage.setItem(LAST_WIP_ID_KEY, trimmedWipId);
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
function isBatchDetail(batch) {
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
  const { data: registryResponse } = useSequenceRegistry();
  const [showWipModal, setShowWipModal] = reactExports.useState(false);
  const [wipError, setWipError] = reactExports.useState(null);
  const [hasPendingChanges, setHasPendingChanges] = reactExports.useState(false);
  const handlePendingChangesChange = reactExports.useCallback((hasPending) => {
    setHasPendingChanges(hasPending);
  }, []);
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
    if (isBatchDetail(batch) && ((_a = batch.execution) == null ? void 0 : _a.steps)) {
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
    if (batch.sequencePackage && (registryResponse == null ? void 0 : registryResponse.items)) {
      const sequenceName = batch.sequencePackage.replace(/^sequences\//, "");
      const registryItem = registryResponse.items.find((r) => r.name === sequenceName);
      if ((registryItem == null ? void 0 : registryItem.status) === "update_available") {
        toast.warning(
          `시퀀스 업데이트가 가능합니다. 현재: v${registryItem.localVersion} → 최신: v${registryItem.remoteVersion}`
        );
      }
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
    useLogStore.getState().clearLogs();
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
    var _a;
    setWipError(null);
    try {
      const processId = batch && isBatchDetail(batch) ? batch.processId ?? ((_a = batch.config) == null ? void 0 : _a.processId) : void 0;
      if (processId === void 0 || processId === null) {
        setWipError("MES Process가 설정되지 않았습니다. Config 탭에서 MES Process를 선택하고 저장해주세요.");
        return;
      }
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
  const elapsedTime = isRunning ? batch.elapsed : batch.elapsed > 0 ? batch.elapsed : isBatchDetail(batch) && batch.execution && batch.execution.elapsed > 0 ? batch.execution.elapsed : (statistics == null ? void 0 : statistics.lastDuration) ?? 0;
  const progress = batch.progress ?? (isBatchDetail(batch) && batch.execution ? batch.execution.progress : 0);
  const getFinalVerdict = () => {
    if (batch.status === "running" || batch.status === "starting") {
      return { text: "In Progress", color: "text-brand-500", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-6 h-6 animate-spin" }) };
    }
    if (batch.status === "completed") {
      if (batch.lastRunPassed) {
        return { text: "PASS", color: "text-green-500", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-6 h-6" }) };
      }
      return { text: "FAIL", color: "text-red-500", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-6 h-6" }) };
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
      panel: /* @__PURE__ */ jsxRuntimeExports.jsx(
        DebugLogPanel,
        {
          batchId: batchId || "",
          steps,
          isRunning,
          onPendingChangesChange: handlePendingChangesChange
        }
      ),
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
              /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge$1, { status: batch.status }),
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
                  disabled: hasPendingChanges,
                  title: hasPendingChanges ? "Save changes in Config/Params tabs first" : void 0,
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-4 h-4 mr-2" }),
                    hasPendingChanges ? "Save Changes First" : "Start Sequence"
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
                variant: batch.status === "completed" ? batch.lastRunPassed ? "success" : "error" : "default"
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
  const stepCount = Math.max(totalSteps || 0, (stepNames == null ? void 0 : stepNames.length) || 0, steps.length);
  const stepResultMap = /* @__PURE__ */ new Map();
  for (const step of steps) {
    stepResultMap.set(step.name, step);
  }
  const displaySteps = Array.from({ length: stepCount }, (_, i) => {
    const placeholderName = (stepNames == null ? void 0 : stepNames[i]) || `Step ${i + 1}`;
    const actualStep = stepResultMap.get(placeholderName);
    if (actualStep) {
      return {
        ...actualStep,
        order: actualStep.order ?? i + 1
      };
    }
    return {
      order: i + 1,
      name: placeholderName,
      status: "pending",
      pass: false,
      duration: void 0,
      result: void 0
    };
  });
  if (displaySteps.length === 0) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: "No steps defined for this sequence" });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "overflow-x-auto", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("table", { className: "w-full text-sm", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("thead", { children: /* @__PURE__ */ jsxRuntimeExports.jsxs("tr", { className: "text-left border-b", style: { color: "var(--color-text-tertiary)", borderColor: "var(--color-border-default)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("th", { className: "pb-3 pr-4 w-12", children: "#" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("th", { className: "pb-3 pr-4", children: "Step Name" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("th", { className: "pb-3 pr-4 w-24", children: "Status" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("th", { className: "pb-3 pr-4 w-20", children: "Result" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("th", { className: "pb-3 pr-4", children: "Measurements" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("th", { className: "pb-3 pr-4 w-28", children: "Duration" })
    ] }) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("tbody", { children: displaySteps.map((step) => /* @__PURE__ */ jsxRuntimeExports.jsx(StepRow$2, { step, onClick: onStepClick ? () => onStepClick(step.name) : void 0 }, `${step.order}-${step.name}`)) })
  ] }) });
}
function MeasurementsCell({ measurements }) {
  if (!measurements || Object.keys(measurements).length === 0) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "-" });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex flex-wrap gap-2", children: Object.entries(measurements).map(([key, val]) => {
    const m = val;
    const value = (m == null ? void 0 : m.value) ?? val;
    const unit = (m == null ? void 0 : m.unit) ?? "";
    const passed = m == null ? void 0 : m.passed;
    const hasLimits = (m == null ? void 0 : m.min) !== void 0 || (m == null ? void 0 : m.max) !== void 0;
    const displayValue = typeof value === "number" ? value.toFixed(2) : String(value);
    const valueColor = passed === true ? "text-green-500" : passed === false ? "text-red-500" : "";
    return /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "span",
      {
        className: "inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono",
        style: { backgroundColor: "var(--color-bg-tertiary)" },
        title: hasLimits ? `${key}: ${displayValue}${unit} (${m.min ?? "-"} ~ ${m.max ?? "-"})` : `${key}: ${displayValue}${unit}`,
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { style: { color: "var(--color-text-tertiary)" }, children: [
            key,
            ":"
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: valueColor, style: !valueColor ? { color: "var(--color-text-primary)" } : void 0, children: [
            displayValue,
            unit
          ] })
        ]
      },
      key
    );
  }) });
}
function StepRow$2({ step, onClick }) {
  var _a;
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
        /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "py-3 pr-4", children: /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge$1, { status: getStatusBadge(), size: "sm" }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "py-3 pr-4", children: getResultBadge() }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "py-3 pr-4", children: /* @__PURE__ */ jsxRuntimeExports.jsx(MeasurementsCell, { measurements: (_a = step.result) == null ? void 0 : _a.measurements }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "py-3 pr-4 font-mono", style: { color: "var(--color-text-secondary)" }, children: step.duration != null ? `${step.duration.toFixed(2)}s` : "-" })
      ]
    }
  );
}
function SequencesPage() {
  var _a;
  const { sequenceName } = useParams();
  const navigate = useNavigate();
  const [filter2, setFilter] = reactExports.useState("all");
  const [dismissedWarning, setDismissedWarning] = reactExports.useState(false);
  const { data: registryResponse, isLoading: listLoading } = useSequenceRegistry();
  const registry = registryResponse == null ? void 0 : registryResponse.items;
  const warnings = registryResponse == null ? void 0 : registryResponse.warnings;
  const { data: selectedSequence, isLoading: detailLoading } = useSequence(sequenceName ?? null);
  const deleteMutation = useDeleteSequence();
  const downloadMutation = useDownloadSequence();
  const pullMutation = usePullSequence();
  const syncMutation = useSyncSequences();
  const { data: autoSyncStatus } = useAutoSyncStatus();
  const configureAutoSync2 = useConfigureAutoSync();
  const handleToggleAutoSync = async () => {
    if (!autoSyncStatus) return;
    try {
      await configureAutoSync2.mutateAsync({
        enabled: !autoSyncStatus.enabled,
        poll_interval: autoSyncStatus.pollInterval,
        auto_pull: autoSyncStatus.autoPull
      });
      toast.success(`Auto-sync ${!autoSyncStatus.enabled ? "활성화" : "비활성화"}됨`);
    } catch {
    }
  };
  const filteredRegistry = reactExports.useMemo(() => {
    if (!registry) return [];
    switch (filter2) {
      case "installed":
        return registry.filter(
          (s) => ["installed_latest", "update_available", "local_only"].includes(s.status)
        );
      case "updates":
        return registry.filter((s) => s.status === "update_available");
      case "not_installed":
        return registry.filter((s) => s.status === "not_installed");
      default:
        return registry;
    }
  }, [registry, filter2]);
  const counts = reactExports.useMemo(() => {
    if (!registry) return { all: 0, installed: 0, updates: 0, not_installed: 0 };
    return {
      all: registry.length,
      installed: registry.filter(
        (s) => ["installed_latest", "update_available", "local_only"].includes(s.status)
      ).length,
      updates: registry.filter((s) => s.status === "update_available").length,
      not_installed: registry.filter((s) => s.status === "not_installed").length
    };
  }, [registry]);
  const handleSelectSequence = (name) => {
    navigate(getSequenceDetailRoute(name));
  };
  const handleCloseSequence = () => {
    navigate(ROUTES.SEQUENCES);
  };
  const handleDelete = async (name) => {
    if (!confirm(`Are you sure you want to delete sequence "${name}"?`)) {
      return;
    }
    try {
      await deleteMutation.mutateAsync(name);
      toast.success(`시퀀스 "${name}" 삭제 완료`);
      if (sequenceName === name) {
        navigate(ROUTES.SEQUENCES);
      }
    } catch {
    }
  };
  const handleDownload = async (name) => {
    try {
      await downloadMutation.mutateAsync(name);
      toast.success(`시퀀스 "${name}" 다운로드 시작`);
    } catch {
    }
  };
  const handlePull = async (name, force = false) => {
    try {
      const result = await pullMutation.mutateAsync({ name, force });
      if (result.updated) {
        toast.success(`시퀀스 "${name}" 업데이트 완료`);
      } else if (!result.needsUpdate) {
        toast.info(`시퀀스 "${name}"는 이미 최신 버전입니다`);
      } else {
        toast.success(`시퀀스 "${name}" 설치 완료`);
      }
    } catch {
    }
  };
  const handleSyncAll = async () => {
    try {
      const result = await syncMutation.mutateAsync(void 0);
      if (result.sequencesFailed > 0) {
        toast.warning(`동기화 완료: ${result.sequencesUpdated}개 업데이트, ${result.sequencesFailed}개 실패`);
      } else if (result.sequencesUpdated > 0) {
        toast.success(`동기화 완료: ${result.sequencesUpdated}개 시퀀스 업데이트됨`);
      } else {
        toast.info("모든 시퀀스가 최신 상태입니다");
      }
    } catch {
    }
  };
  if (listLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingOverlay, { message: "Loading sequences..." });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    warnings && warnings.length > 0 && !dismissedWarning && /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "flex items-start gap-3 p-4 rounded-lg border",
        style: {
          backgroundColor: "rgba(251, 191, 36, 0.1)",
          borderColor: "rgba(251, 191, 36, 0.3)"
        },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "text-sm font-medium text-amber-500", children: "백엔드 연결 문제" }),
            warnings.map((warning, index) => /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-1", style: { color: "var(--color-text-secondary)" }, children: warning }, index))
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "button",
            {
              onClick: () => setDismissedWarning(true),
              className: "p-1 rounded hover:bg-amber-500/20 transition-colors",
              children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-4 h-4 text-amber-500" })
            }
          )
        ]
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(GitBranch, { className: "w-6 h-6 text-brand-500" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: "Sequences" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "button",
            {
              onClick: handleToggleAutoSync,
              disabled: configureAutoSync2.isPending,
              className: "flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors",
              style: {
                backgroundColor: (autoSyncStatus == null ? void 0 : autoSyncStatus.enabled) ? "rgba(34, 197, 94, 0.1)" : "var(--color-bg-tertiary)",
                border: `1px solid ${(autoSyncStatus == null ? void 0 : autoSyncStatus.enabled) ? "rgba(34, 197, 94, 0.3)" : "var(--color-border-default)"}`
              },
              children: [
                (autoSyncStatus == null ? void 0 : autoSyncStatus.enabled) ? /* @__PURE__ */ jsxRuntimeExports.jsx(ToggleRight, { className: "w-5 h-5 text-green-500" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(ToggleLeft, { className: "w-5 h-5", style: { color: "var(--color-text-secondary)" } }),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "span",
                  {
                    className: "text-sm font-medium",
                    style: { color: (autoSyncStatus == null ? void 0 : autoSyncStatus.enabled) ? "#22c55e" : "var(--color-text-secondary)" },
                    children: "Auto-sync"
                  }
                ),
                (autoSyncStatus == null ? void 0 : autoSyncStatus.running) && /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "w-3 h-3 text-green-500 animate-spin" })
              ]
            }
          ),
          (autoSyncStatus == null ? void 0 : autoSyncStatus.enabled) && autoSyncStatus.lastCheckAt && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: [
            "Last: ",
            new Date(autoSyncStatus.lastCheckAt).toLocaleTimeString()
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          Button,
          {
            variant: "secondary",
            onClick: handleSyncAll,
            disabled: syncMutation.isPending,
            children: [
              syncMutation.isPending ? /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "sm", className: "mr-2" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(CloudDownload, { className: "w-4 h-4 mr-2" }),
              "Sync All"
            ]
          }
        )
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        FilterTab,
        {
          label: "All",
          count: counts.all,
          active: filter2 === "all",
          onClick: () => setFilter("all")
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        FilterTab,
        {
          label: "Installed",
          count: counts.installed,
          active: filter2 === "installed",
          onClick: () => setFilter("installed")
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        FilterTab,
        {
          label: "Updates",
          count: counts.updates,
          active: filter2 === "updates",
          onClick: () => setFilter("updates"),
          highlight: counts.updates > 0
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        FilterTab,
        {
          label: "Not Installed",
          count: counts.not_installed,
          active: filter2 === "not_installed",
          onClick: () => setFilter("not_installed")
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6 items-start", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: filter2 === "all" ? `All Sequences (${filteredRegistry.length})` : filter2 === "installed" ? `Installed (${filteredRegistry.length})` : filter2 === "updates" ? `Updates Available (${filteredRegistry.length})` : `Available to Install (${filteredRegistry.length})` }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          SequenceList,
          {
            sequences: filteredRegistry,
            selectedName: sequenceName,
            onSelect: handleSelectSequence,
            onDelete: handleDelete,
            onDownload: handleDownload,
            onPull: handlePull,
            isDeleting: deleteMutation.isPending,
            isDownloading: downloadMutation.isPending,
            isPulling: pullMutation.isPending
          }
        )
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: "Sequence Details" }),
        sequenceName ? /* @__PURE__ */ jsxRuntimeExports.jsx(
          SequenceDetail,
          {
            sequence: selectedSequence ?? null,
            registryItem: ((_a = registryResponse == null ? void 0 : registryResponse.items) == null ? void 0 : _a.find((r) => r.name === sequenceName)) ?? null,
            isLoading: detailLoading,
            onClose: handleCloseSequence,
            onDelete: () => handleDelete(sequenceName),
            onDownload: () => handleDownload(sequenceName),
            onPull: (force) => handlePull(sequenceName, force),
            isPulling: pullMutation.isPending
          }
        ) : /* @__PURE__ */ jsxRuntimeExports.jsx(
          "div",
          {
            className: "p-8 rounded-lg border text-center",
            style: {
              backgroundColor: "var(--color-bg-secondary)",
              borderColor: "var(--color-border-default)"
            },
            children: /* @__PURE__ */ jsxRuntimeExports.jsx("p", { style: { color: "var(--color-text-tertiary)" }, children: "Select a sequence to view details" })
          }
        )
      ] })
    ] })
  ] });
}
function FilterTab({ label, count, active, onClick, highlight }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "button",
    {
      onClick,
      className: "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
      style: {
        backgroundColor: active ? "var(--color-brand-500)" : "var(--color-bg-secondary)",
        color: active ? "white" : highlight ? "var(--color-warning-text)" : "var(--color-text-secondary)",
        border: `1px solid ${active ? "var(--color-brand-500)" : highlight ? "var(--color-warning-border)" : "var(--color-border-default)"}`
      },
      children: [
        label,
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "span",
          {
            className: "ml-2 px-2 py-0.5 rounded-full text-xs",
            style: {
              backgroundColor: active ? "rgba(255,255,255,0.2)" : "var(--color-bg-tertiary)"
            },
            children: count
          }
        )
      ]
    }
  );
}
function StatusBadge({ status }) {
  const config = {
    installed_latest: {
      icon: CircleCheckBig,
      label: "Up to date",
      color: "text-green-500",
      bg: "bg-green-500/10"
    },
    update_available: {
      icon: CircleArrowUp,
      label: "Update available",
      color: "text-amber-500",
      bg: "bg-amber-500/10"
    },
    not_installed: {
      icon: Circle,
      label: "Not installed",
      color: "text-zinc-400",
      bg: "bg-zinc-500/10"
    },
    local_only: {
      icon: CircleDot,
      label: "Local only",
      color: "text-blue-400",
      bg: "bg-blue-500/10"
    }
  };
  const { icon: Icon2, label, color, bg } = config[status];
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: `inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs ${color} ${bg}`, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(Icon2, { className: "w-3 h-3" }),
    label
  ] });
}
function SequenceList({
  sequences,
  selectedName,
  onSelect,
  onDelete,
  onDownload,
  onPull,
  isDeleting,
  isDownloading,
  isPulling
}) {
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { children: sequences.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "p-8 text-center rounded-lg border",
      style: {
        backgroundColor: "var(--color-bg-secondary)",
        borderColor: "var(--color-border-default)",
        color: "var(--color-text-tertiary)"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { children: "No sequences found" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-2", children: "Try a different filter or sync from server" })
      ]
    }
  ) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2", children: sequences.map((seq) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "p-4 rounded-lg border transition-colors",
      style: {
        backgroundColor: selectedName === seq.name ? "rgba(var(--color-brand-rgb), 0.1)" : "var(--color-bg-secondary)",
        borderColor: selectedName === seq.name ? "rgba(var(--color-brand-rgb), 0.5)" : "var(--color-border-default)"
      },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("button", { onClick: () => onSelect(seq.name), className: "w-full text-left", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "font-medium", style: { color: "var(--color-text-primary)" }, children: seq.displayName || seq.name }),
                /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge, { status: seq.status })
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-1", style: { color: "var(--color-text-tertiary)" }, children: seq.name })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(VersionDisplay, { item: seq }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronRight, { className: "w-4 h-4", style: { color: "var(--color-text-secondary)" } })
            ] })
          ] }),
          seq.description && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mt-2 line-clamp-2", style: { color: "var(--color-text-secondary)" }, children: seq.description })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 mt-3 pt-3 border-t", style: { borderColor: "var(--color-border-subtle)" }, children: [
          seq.status === "not_installed" && /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "button",
            {
              onClick: (e) => {
                e.stopPropagation();
                onPull(seq.name);
              },
              disabled: isPulling,
              className: "flex items-center gap-1 px-2 py-1 text-xs rounded transition-colors text-brand-400 hover:text-brand-300 hover:bg-brand-500/10 disabled:opacity-50",
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(CloudDownload, { className: "w-3 h-3" }),
                "Install"
              ]
            }
          ),
          seq.status === "update_available" && /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "button",
            {
              onClick: (e) => {
                e.stopPropagation();
                onPull(seq.name);
              },
              disabled: isPulling,
              className: "flex items-center gap-1 px-2 py-1 text-xs rounded transition-colors text-amber-400 hover:text-amber-300 hover:bg-amber-500/10 disabled:opacity-50",
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(CircleArrowUp, { className: "w-3 h-3" }),
                "Update"
              ]
            }
          ),
          ["installed_latest", "update_available", "local_only"].includes(seq.status) && /* @__PURE__ */ jsxRuntimeExports.jsxs(
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
          ["installed_latest", "update_available", "local_only"].includes(seq.status) && /* @__PURE__ */ jsxRuntimeExports.jsxs(
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
function VersionDisplay({ item }) {
  if (item.status === "update_available") {
    return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1 text-xs", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { style: { color: "var(--color-text-tertiary)" }, children: [
        "v",
        item.localVersion
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(ArrowRight, { className: "w-3 h-3 text-amber-500" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-amber-500", children: [
        "v",
        item.remoteVersion
      ] })
    ] });
  }
  if (item.status === "not_installed") {
    return /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "span",
      {
        className: "text-xs px-2 py-1 rounded",
        style: { backgroundColor: "var(--color-bg-tertiary)", color: "var(--color-text-secondary)" },
        children: [
          "v",
          item.remoteVersion
        ]
      }
    );
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "span",
    {
      className: "text-xs px-2 py-1 rounded",
      style: { backgroundColor: "var(--color-bg-tertiary)", color: "var(--color-text-secondary)" },
      children: [
        "v",
        item.localVersion
      ]
    }
  );
}
function SequenceDetail({
  sequence,
  registryItem,
  isLoading,
  onClose,
  onDelete,
  onDownload,
  onPull,
  isPulling
}) {
  const [activeTab, setActiveTab] = reactExports.useState("steps");
  if (isLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "p-8 flex items-center justify-center rounded-lg border",
        style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" },
        children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "lg" })
      }
    );
  }
  if ((registryItem == null ? void 0 : registryItem.status) === "not_installed") {
    return /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "p-8 rounded-lg border text-center",
        style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(CloudDownload, { className: "w-12 h-12 mx-auto mb-4", style: { color: "var(--color-text-tertiary)" } }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "text-lg font-medium mb-2", style: { color: "var(--color-text-primary)" }, children: registryItem.displayName || registryItem.name }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm mb-4", style: { color: "var(--color-text-secondary)" }, children: registryItem.description || "This sequence is not installed yet." }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "primary", onClick: () => onPull(false), disabled: isPulling, children: [
            isPulling ? /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "sm", className: "mr-2" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(CloudDownload, { className: "w-4 h-4 mr-2" }),
            "Install v",
            registryItem.remoteVersion
          ] })
        ]
      }
    );
  }
  if (!sequence) {
    return null;
  }
  const defaultParameters = sequence.parameters.reduce(
    (acc, p) => ({ ...acc, [p.name]: p.default }),
    {}
  );
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "rounded-lg border",
      style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-default)" },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 border-b", style: { borderColor: "var(--color-border-default)" }, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: sequence.displayName }),
                registryItem && /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge, { status: registryItem.status })
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: [
                sequence.name,
                " v",
                sequence.version,
                (registryItem == null ? void 0 : registryItem.status) === "update_available" && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-amber-500 ml-2", children: [
                  "(v",
                  registryItem.remoteVersion,
                  " available)"
                ] })
              ] })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
              (registryItem == null ? void 0 : registryItem.status) === "update_available" && /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "primary", size: "sm", onClick: () => onPull(false), disabled: isPulling, children: isPulling ? /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "sm" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(CircleArrowUp, { className: "w-4 h-4" }) }),
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
          activeTab === "test" && /* @__PURE__ */ jsxRuntimeExports.jsx(TestTabContent, { sequenceName: sequence.name, defaultParameters })
        ] })
      ]
    }
  );
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
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "span",
          {
            className: "w-6 h-6 flex items-center justify-center text-xs font-medium rounded-full",
            style: { backgroundColor: "var(--color-bg-secondary)", color: "var(--color-text-secondary)" },
            children: step.order
          }
        ),
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
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "span",
        {
          className: "text-xs px-2 py-0.5 rounded",
          style: { backgroundColor: "var(--color-bg-secondary)", color: "var(--color-text-secondary)" },
          children: param.type
        }
      )
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
      if (simResult.status === "completed") {
        toast.success(`${mode === "preview" ? "Preview" : "Dry run"} 완료`);
      }
    } catch {
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
                result: (_a = result.stepResults) == null ? void 0 : _a.find((r) => r.name === step.name)
              },
              step.name
            );
          })
        ] }),
        result.error && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-2 bg-red-500/10 rounded text-xs text-red-400", children: [
          "Error: ",
          result.error
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "flex items-center gap-4 text-xs pt-2 border-t",
            style: { color: "var(--color-text-tertiary)", borderColor: "var(--color-border-default)" },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
                "ID: ",
                result.id
              ] }),
              result.completedAt && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex items-center gap-1", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-3 h-3" }),
                new Date(result.completedAt).toLocaleTimeString()
              ] })
            ]
          }
        )
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
function ManualControlPage() {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
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
    /* @__PURE__ */ jsxRuntimeExports.jsx(ManualTestTab, {})
  ] });
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
function ManualTestTab() {
  const { data: sequences, isLoading: loadingSequences } = useSequenceList();
  const [selectedSequence, setSelectedSequence] = reactExports.useState("");
  const [sessionId, setSessionId] = reactExports.useState(null);
  const [parameterValues, setParameterValues] = reactExports.useState({});
  const [mockMode, setMockMode] = reactExports.useState(false);
  const [debugLogs, setDebugLogs] = reactExports.useState([]);
  const [showDebugPanel, setShowDebugPanel] = reactExports.useState(true);
  const logIdRef = reactExports.useRef(0);
  const logContainerRef = reactExports.useRef(null);
  const addLog = reactExports.useCallback((level, message, data) => {
    setDebugLogs((prev) => {
      const newLog = {
        id: ++logIdRef.current,
        timestamp: /* @__PURE__ */ new Date(),
        level,
        message,
        data
      };
      const updated = [...prev, newLog].slice(-100);
      return updated;
    });
  }, []);
  reactExports.useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [debugLogs]);
  const clearLogs = reactExports.useCallback(() => {
    setDebugLogs([]);
  }, []);
  const { data: sequenceDetails } = useSequence(selectedSequence || null);
  const manualSessionQuery = useManualSession(mockMode ? null : sessionId);
  const createManualSession2 = useCreateManualSession();
  const initializeManualSession2 = useInitializeManualSession();
  const finalizeManualSession2 = useFinalizeManualSession();
  const abortManualSession2 = useAbortManualSession();
  const deleteManualSession2 = useDeleteManualSession();
  const runManualStep2 = useRunManualStep();
  const skipManualStep2 = useSkipManualStep();
  const simulationSessionQuery = useSimulationSession(mockMode ? sessionId : null);
  const createSimulationSession2 = useCreateSimulationSession();
  const initializeSimulationSession2 = useInitializeSimulationSession();
  const finalizeSimulationSession2 = useFinalizeSimulationSession();
  const abortSimulationSession2 = useAbortSimulationSession();
  const deleteSimulationSession2 = useDeleteSimulationSession();
  const runSimulationStep2 = useRunSimulationStep();
  const skipSimulationStep2 = useSkipSimulationStep();
  const session = mockMode ? simulationSessionQuery.data : manualSessionQuery.data;
  const loadingSession = mockMode ? simulationSessionQuery.isLoading : manualSessionQuery.isLoading;
  const sequenceOptions = reactExports.useMemo(() => {
    return (sequences == null ? void 0 : sequences.map((s) => ({
      value: s.name,
      label: `${s.displayName} (v${s.version})`
    }))) ?? [];
  }, [sequences]);
  const handleCreateSession = async () => {
    if (!selectedSequence) return;
    clearLogs();
    try {
      const params = {};
      if (sequenceDetails == null ? void 0 : sequenceDetails.parameters) {
        for (const param of sequenceDetails.parameters) {
          params[param.name] = parameterValues[param.name] ?? param.default;
        }
      }
      const modeLabel = mockMode ? "[Mock]" : "[Hardware]";
      addLog("info", `${modeLabel} Creating session for "${selectedSequence}"...`, { params, mockMode });
      const newSession = mockMode ? await createSimulationSession2.mutateAsync({
        sequenceName: selectedSequence,
        parameters: Object.keys(params).length > 0 ? params : void 0
      }) : await createManualSession2.mutateAsync({
        sequenceName: selectedSequence,
        parameters: Object.keys(params).length > 0 ? params : void 0
      });
      setSessionId(newSession.id);
      addLog("success", `Session created: ${newSession.id}`, {
        status: newSession.status,
        steps: newSession.steps.length
      });
    } catch (error) {
      addLog("error", `Failed to create session: ${getErrorMessage(error)}`, error);
    }
  };
  const handleInitialize = async () => {
    if (!sessionId) return;
    clearLogs();
    try {
      if (mockMode) {
        addLog("info", "Initializing simulation session...");
        const result = await initializeSimulationSession2.mutateAsync(sessionId);
        addLog("success", `Session initialized.`, { status: result.status });
      } else {
        addLog("info", "Initializing session (connecting hardware)...");
        const result = await initializeManualSession2.mutateAsync(sessionId);
        const hwConnected = result.hardware.filter((h) => h.connected).length;
        addLog("success", `Session initialized. Hardware: ${hwConnected}/${result.hardware.length} connected`, {
          status: result.status,
          hardware: result.hardware.map((h) => ({ id: h.id, connected: h.connected, error: h.error }))
        });
      }
    } catch (error) {
      addLog("error", `Failed to initialize session: ${getErrorMessage(error)}`, error);
    }
  };
  const handleFinalize = async () => {
    if (!sessionId) return;
    try {
      addLog("info", "Finalizing session...");
      const result = mockMode ? await finalizeSimulationSession2.mutateAsync(sessionId) : await finalizeManualSession2.mutateAsync(sessionId);
      addLog("success", `Session finalized. Overall: ${result.overallPass ? "PASS" : "FAIL"}`, {
        status: result.status,
        overallPass: result.overallPass
      });
    } catch (error) {
      addLog("error", `Failed to finalize session: ${getErrorMessage(error)}`, error);
    }
  };
  const handleAbort = async () => {
    if (!sessionId) return;
    try {
      addLog("warning", "Aborting session...");
      if (mockMode) {
        await abortSimulationSession2.mutateAsync(sessionId);
      } else {
        await abortManualSession2.mutateAsync(sessionId);
      }
      addLog("warning", "Session aborted");
    } catch (error) {
      addLog("error", `Failed to abort session: ${getErrorMessage(error)}`, error);
    }
  };
  const handleReset = async () => {
    if (sessionId) {
      if (mockMode) {
        await deleteSimulationSession2.mutateAsync(sessionId);
      } else {
        await deleteManualSession2.mutateAsync(sessionId);
      }
    }
    setSessionId(null);
    setSelectedSequence("");
    setParameterValues({});
    clearLogs();
  };
  const handleRunStep = async (stepName) => {
    if (!sessionId) return;
    try {
      const overrides = Object.keys(parameterValues).length > 0 ? parameterValues : void 0;
      if (overrides) {
        addLog("info", `Running step: ${stepName} with parameter overrides...`, overrides);
      } else {
        addLog("info", `Running step: ${stepName}...`);
      }
      const result = mockMode ? await runSimulationStep2.mutateAsync({ sessionId, stepName, parameterOverrides: overrides }) : await runManualStep2.mutateAsync({ sessionId, stepName, parameterOverrides: overrides });
      if (result.status === "passed") {
        addLog("success", `Step "${stepName}" passed (${result.duration.toFixed(2)}s)`, {
          measurements: result.measurements,
          result: result.result
        });
      } else {
        addLog("error", `Step "${stepName}" failed: ${result.error}`, {
          measurements: result.measurements,
          error: result.error
        });
      }
    } catch (error) {
      addLog("error", `Failed to run step "${stepName}": ${getErrorMessage(error)}`, error);
    }
  };
  const handleSkipStep = async (stepName) => {
    if (!sessionId) return;
    try {
      addLog("warning", `Skipping step: ${stepName}`);
      if (mockMode) {
        await skipSimulationStep2.mutateAsync({ sessionId, stepName });
      } else {
        await skipManualStep2.mutateAsync({ sessionId, stepName });
      }
      addLog("info", `Step "${stepName}" skipped`);
    } catch (error) {
      addLog("error", `Failed to skip step "${stepName}": ${getErrorMessage(error)}`, error);
    }
  };
  const handleSequenceChange = (sequenceName) => {
    setSelectedSequence(sequenceName);
    setParameterValues({});
  };
  const handleParameterChange = (name, value) => {
    setParameterValues((prev) => ({ ...prev, [name]: value }));
  };
  const isCreated = (session == null ? void 0 : session.status) === "created";
  const isConnecting = (session == null ? void 0 : session.status) === "connecting";
  const isReady = (session == null ? void 0 : session.status) === "ready";
  const isRunning = (session == null ? void 0 : session.status) === "running";
  const isActive = isReady || isRunning;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "p-4 rounded-lg border",
        style: {
          backgroundColor: "var(--color-bg-secondary)",
          borderColor: "var(--color-border-default)"
        },
        children: !session ? /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "h3",
            {
              className: "text-lg font-semibold",
              style: { color: "var(--color-text-primary)" },
              children: "Create Test Session"
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-4 items-end", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex-1", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
              Select,
              {
                label: "Select Sequence",
                options: sequenceOptions,
                value: selectedSequence,
                onChange: (e) => handleSequenceChange(e.target.value),
                placeholder: "Choose a sequence...",
                disabled: loadingSequences
              }
            ) }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("label", { className: "flex items-center gap-2 cursor-pointer select-none", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "input",
                  {
                    type: "checkbox",
                    checked: mockMode,
                    onChange: (e) => setMockMode(e.target.checked),
                    className: "sr-only peer"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "div",
                  {
                    className: cn(
                      "w-11 h-6 rounded-full transition-colors",
                      mockMode ? "bg-brand-500" : "bg-gray-600"
                    )
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "div",
                  {
                    className: cn(
                      "absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform",
                      mockMode && "translate-x-5"
                    )
                  }
                )
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "span",
                {
                  className: "text-sm font-medium flex items-center gap-1",
                  style: { color: mockMode ? "var(--color-brand-500)" : "var(--color-text-secondary)" },
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(FlaskConical, { className: "w-4 h-4" }),
                    "Mock"
                  ]
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              Button,
              {
                variant: "primary",
                onClick: handleCreateSession,
                isLoading: mockMode ? createSimulationSession2.isPending : createManualSession2.isPending,
                disabled: !selectedSequence,
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Terminal, { className: "w-4 h-4 mr-2" }),
                  "Create Session"
                ]
              }
            )
          ] })
        ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "h3",
                {
                  className: "text-lg font-semibold",
                  style: { color: "var(--color-text-primary)" },
                  children: [
                    session.sequenceName,
                    /* @__PURE__ */ jsxRuntimeExports.jsxs(
                      "span",
                      {
                        className: "ml-2 text-sm font-normal",
                        style: { color: "var(--color-text-tertiary)" },
                        children: [
                          "v",
                          session.sequenceVersion
                        ]
                      }
                    )
                  ]
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mt-1", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  StatusBadge$1,
                  {
                    status: session.status === "completed" && session.overallPass ? "pass" : session.status === "completed" && !session.overallPass ? "fail" : session.status === "ready" ? "idle" : session.status === "running" ? "running" : session.status === "connecting" ? "running" : session.status === "failed" ? "error" : "idle",
                    size: "sm"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  "span",
                  {
                    className: "text-sm",
                    style: { color: "var(--color-text-tertiary)" },
                    children: [
                      "Session: ",
                      session.id
                    ]
                  }
                )
              ] })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2", children: [
              isCreated && /* @__PURE__ */ jsxRuntimeExports.jsx(
                Button,
                {
                  variant: "primary",
                  onClick: handleInitialize,
                  isLoading: mockMode ? initializeSimulationSession2.isPending : initializeManualSession2.isPending || isConnecting,
                  children: mockMode ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-4 h-4 mr-1" }),
                    "Initialize"
                  ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(Plug, { className: "w-4 h-4 mr-1" }),
                    "Connect & Initialize"
                  ] })
                }
              ),
              isActive && /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  Button,
                  {
                    variant: "secondary",
                    onClick: handleFinalize,
                    isLoading: mockMode ? finalizeSimulationSession2.isPending : finalizeManualSession2.isPending,
                    children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { className: "w-4 h-4 mr-1" }),
                      "Finalize"
                    ]
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  Button,
                  {
                    variant: "ghost",
                    onClick: handleAbort,
                    isLoading: mockMode ? abortSimulationSession2.isPending : abortManualSession2.isPending,
                    children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsx(CircleStop, { className: "w-4 h-4 mr-1" }),
                      "Abort"
                    ]
                  }
                )
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "ghost", onClick: handleReset, children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "w-4 h-4 mr-1" }),
                "Reset"
              ] })
            ] })
          ] }),
          !mockMode && "hardware" in session && session.hardware.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex flex-wrap gap-2", children: session.hardware.map((hw) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "div",
            {
              className: cn(
                "flex items-center gap-2 px-3 py-1.5 rounded-md text-sm",
                hw.connected ? "bg-green-500/10 border border-green-500/30" : "bg-gray-500/10 border border-gray-500/30"
              ),
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  Plug,
                  {
                    className: cn(
                      "w-4 h-4",
                      hw.connected ? "text-green-500" : "text-gray-500"
                    )
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: hw.displayName }),
                hw.error && /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-red-400 text-xs", children: [
                  "(",
                  hw.error,
                  ")"
                ] })
              ]
            },
            hw.id
          )) }),
          session.steps.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex justify-between text-xs", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: "Progress" }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { style: { color: "var(--color-text-tertiary)" }, children: [
                session.steps.filter((s) => s.status !== "pending").length,
                " /",
                " ",
                session.steps.length,
                " steps"
              ] })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "div",
              {
                className: "h-2 rounded-full overflow-hidden",
                style: { backgroundColor: "var(--color-bg-tertiary)" },
                children: /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "div",
                  {
                    className: "h-full bg-brand-500 transition-all duration-300",
                    style: {
                      width: `${session.steps.filter((s) => s.status !== "pending").length / session.steps.length * 100}%`
                    }
                  }
                )
              }
            )
          ] })
        ] })
      }
    ),
    session && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "p-4 rounded-lg border",
          style: {
            backgroundColor: "var(--color-bg-secondary)",
            borderColor: "var(--color-border-default)"
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "h3",
              {
                className: "text-lg font-semibold mb-4 flex items-center gap-2",
                style: { color: "var(--color-text-primary)" },
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(ListOrdered, { className: "w-5 h-5" }),
                  "Test Steps"
                ]
              }
            ),
            loadingSession ? /* @__PURE__ */ jsxRuntimeExports.jsx(
              "p",
              {
                className: "text-sm text-center py-4",
                style: { color: "var(--color-text-tertiary)" },
                children: "Loading session..."
              }
            ) : session.steps.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx(
              "p",
              {
                className: "text-sm text-center py-4",
                style: { color: "var(--color-text-tertiary)" },
                children: "No steps available"
              }
            ) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2 max-h-[500px] overflow-y-auto", children: session.steps.map((step, index) => {
              const isSkippable = "skippable" in step ? step.skippable : true;
              return /* @__PURE__ */ jsxRuntimeExports.jsx(
                ManualTestStepCard,
                {
                  step: {
                    ...step,
                    skippable: isSkippable,
                    parameterOverrides: "parameterOverrides" in step ? step.parameterOverrides : []
                  },
                  index,
                  isCurrent: index === session.currentStepIndex,
                  canRun: isReady && step.status === "pending",
                  canSkip: isReady && step.status === "pending" && isSkippable,
                  onRun: () => handleRunStep(step.name),
                  onSkip: () => handleSkipStep(step.name),
                  isRunning: mockMode ? runSimulationStep2.isPending : runManualStep2.isPending
                },
                step.name
              );
            }) }),
            session && isReady && session.steps.some((s) => s.status === "pending") && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "mt-4", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(
              Button,
              {
                className: "w-full",
                onClick: async () => {
                  for (const step of session.steps) {
                    if (step.status === "pending") {
                      await handleRunStep(step.name);
                    }
                  }
                },
                isLoading: mockMode ? runSimulationStep2.isPending : runManualStep2.isPending,
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(FastForward, { className: "w-4 h-4 mr-1" }),
                  "Run All Remaining"
                ]
              }
            ) })
          ]
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "p-4 rounded-lg border",
          style: {
            backgroundColor: "var(--color-bg-secondary)",
            borderColor: "var(--color-border-default)"
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "h3",
              {
                className: "text-lg font-semibold mb-4 flex items-center gap-2",
                style: { color: "var(--color-text-primary)" },
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Settings, { className: "w-5 h-5" }),
                  "Parameters"
                ]
              }
            ),
            (sequenceDetails == null ? void 0 : sequenceDetails.parameters) && sequenceDetails.parameters.length > 0 ? /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4 max-h-[500px] overflow-y-auto", children: [
              sequenceDetails.parameters.map((param) => {
                var _a;
                const currentValue = parameterValues[param.name] ?? ((_a = session.parameters) == null ? void 0 : _a[param.name]) ?? param.default;
                return /* @__PURE__ */ jsxRuntimeExports.jsx(
                  ParameterInput,
                  {
                    param,
                    value: currentValue,
                    onChange: (value) => handleParameterChange(param.name, value)
                  },
                  param.name
                );
              }),
              Object.keys(parameterValues).length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx(
                "p",
                {
                  className: "text-xs italic",
                  style: { color: "var(--color-text-tertiary)" },
                  children: "* Modified parameters will be applied to next step execution"
                }
              )
            ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx(
              "p",
              {
                className: "text-sm text-center py-4",
                style: { color: "var(--color-text-tertiary)" },
                children: "No parameters configured"
              }
            )
          ]
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "p-4 rounded-lg border",
          style: {
            backgroundColor: "var(--color-bg-secondary)",
            borderColor: "var(--color-border-default)"
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-3", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "h3",
                {
                  className: "text-lg font-semibold flex items-center gap-2",
                  style: { color: "var(--color-text-primary)" },
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(Bug, { className: "w-5 h-5" }),
                    "Debug Logs"
                  ]
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  Button,
                  {
                    size: "sm",
                    variant: "ghost",
                    onClick: () => setShowDebugPanel(!showDebugPanel),
                    children: showDebugPanel ? /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronUp, { className: "w-4 h-4" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronDown, { className: "w-4 h-4" })
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  Button,
                  {
                    size: "sm",
                    variant: "ghost",
                    onClick: clearLogs,
                    disabled: debugLogs.length === 0,
                    children: /* @__PURE__ */ jsxRuntimeExports.jsx(Trash2, { className: "w-4 h-4" })
                  }
                )
              ] })
            ] }),
            showDebugPanel && /* @__PURE__ */ jsxRuntimeExports.jsx(
              "div",
              {
                ref: logContainerRef,
                className: "font-mono text-xs space-y-1 max-h-[500px] overflow-y-auto p-2 rounded",
                style: { backgroundColor: "var(--color-bg-tertiary)" },
                children: debugLogs.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "p",
                  {
                    className: "text-center py-4",
                    style: { color: "var(--color-text-tertiary)" },
                    children: "No logs yet. Actions will be logged here."
                  }
                ) : debugLogs.map((log2) => /* @__PURE__ */ jsxRuntimeExports.jsx(DebugLogRow, { log: log2 }, log2.id))
              }
            )
          ]
        }
      )
    ] })
  ] });
}
function DebugLogRow({ log: log2 }) {
  const [isExpanded, setIsExpanded] = reactExports.useState(false);
  const levelColors = {
    info: "text-blue-400",
    success: "text-green-400",
    warning: "text-yellow-400",
    error: "text-red-400"
  };
  const levelLabels = {
    info: "INFO",
    success: "PASS",
    warning: "WARN",
    error: "ERR "
  };
  const formatTimestamp2 = (date) => {
    const time = date.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    });
    const ms = String(date.getMilliseconds()).padStart(3, "0");
    return `${time}.${ms}`;
  };
  const hasData = log2.data !== void 0 && log2.data !== null;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "py-1 border-b last:border-b-0",
      style: { borderColor: "var(--color-border-default)" },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-start gap-2", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-tertiary)" }, children: formatTimestamp2(log2.timestamp) }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: cn("font-bold", levelColors[log2.level]), children: [
            "[",
            levelLabels[log2.level],
            "]"
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "span",
            {
              className: "flex-1",
              style: { color: "var(--color-text-primary)" },
              children: log2.message
            }
          ),
          hasData && /* @__PURE__ */ jsxRuntimeExports.jsx(
            "button",
            {
              onClick: () => setIsExpanded(!isExpanded),
              className: "px-1 hover:bg-white/10 rounded",
              style: { color: "var(--color-text-tertiary)" },
              children: isExpanded ? "[-]" : "[+]"
            }
          )
        ] }),
        isExpanded && hasData && /* @__PURE__ */ jsxRuntimeExports.jsx(
          "pre",
          {
            className: "mt-1 ml-20 p-2 rounded text-xs overflow-auto max-h-32",
            style: {
              backgroundColor: "var(--color-bg-secondary)",
              color: "var(--color-text-secondary)"
            },
            children: JSON.stringify(log2.data, null, 2)
          }
        )
      ]
    }
  );
}
function ManualTestStepCard({
  step,
  index,
  isCurrent,
  canRun,
  canSkip,
  onRun,
  onSkip,
  isRunning
}) {
  const [isExpanded, setIsExpanded] = reactExports.useState(false);
  const statusColors = {
    pending: "border-gray-500/30",
    running: "border-blue-500 bg-blue-500/10",
    passed: "border-green-500 bg-green-500/10",
    failed: "border-red-500 bg-red-500/10",
    skipped: "border-gray-500 bg-gray-500/10"
  };
  const StatusIcon = {
    pending: Clock,
    running: Play,
    passed: CircleCheckBig,
    failed: CircleX,
    skipped: SkipForward
  }[step.status] ?? Clock;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: cn(
        "p-3 rounded-lg border transition-all",
        statusColors[step.status] ?? "border-gray-500/30",
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
                  step.status === "passed" && "text-green-500",
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
              step.duration > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "span",
                {
                  className: "ml-2 text-xs",
                  style: { color: "var(--color-text-tertiary)" },
                  children: [
                    step.duration.toFixed(2),
                    "s"
                  ]
                }
              )
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
            canRun && /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { size: "sm", onClick: onRun, isLoading: isRunning, children: /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-3 h-3" }) }),
            canSkip && /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { size: "sm", variant: "ghost", onClick: onSkip, children: "Skip" }),
            (step.result || step.error || Object.keys(step.measurements).length > 0) && /* @__PURE__ */ jsxRuntimeExports.jsx(
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
            className: "mt-3 pt-3 border-t space-y-2",
            style: { borderColor: "var(--color-border-default)" },
            children: [
              step.error && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-2 rounded bg-red-500/10 text-red-400 text-sm", children: [
                "Error: ",
                step.error
              ] }),
              Object.keys(step.measurements).length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "h4",
                  {
                    className: "text-sm font-medium mb-1",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Measurements"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid grid-cols-2 gap-2", children: Object.entries(step.measurements).map(([key, value]) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  "div",
                  {
                    className: "p-2 rounded text-sm",
                    style: { backgroundColor: "var(--color-bg-tertiary)" },
                    children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { style: { color: "var(--color-text-tertiary)" }, children: [
                        key,
                        ":"
                      ] }),
                      " ",
                      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-primary)" }, children: formatResult(value) })
                    ]
                  },
                  key
                )) })
              ] }),
              step.result && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
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
function ParameterInput({ param, value, onChange }) {
  const handleChange = (e) => {
    const rawValue = e.target.value;
    switch (param.type) {
      case "float":
        onChange(rawValue === "" ? param.default : parseFloat(rawValue));
        break;
      case "integer":
        onChange(rawValue === "" ? param.default : parseInt(rawValue, 10));
        break;
      case "boolean":
        onChange(rawValue === "true");
        break;
      default:
        onChange(rawValue);
    }
  };
  const inputClasses = cn(
    "w-full px-3 py-2 rounded-md text-sm",
    "border transition-colors",
    "focus:outline-none focus:ring-2 focus:ring-brand-500/50"
  );
  const inputStyle = {
    backgroundColor: "var(--color-bg-secondary)",
    borderColor: "var(--color-border-default)",
    color: "var(--color-text-primary)"
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "label",
      {
        className: "text-sm font-medium flex items-center gap-2",
        style: { color: "var(--color-text-secondary)" },
        children: [
          param.displayName,
          param.unit && /* @__PURE__ */ jsxRuntimeExports.jsx(
            "span",
            {
              className: "text-xs px-1.5 py-0.5 rounded",
              style: {
                backgroundColor: "var(--color-bg-secondary)",
                color: "var(--color-text-tertiary)"
              },
              children: param.unit
            }
          )
        ]
      }
    ),
    param.type === "boolean" ? /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "select",
      {
        className: inputClasses,
        style: inputStyle,
        value: String(value),
        onChange: handleChange,
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "true", children: "True" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "false", children: "False" })
        ]
      }
    ) : param.options && param.options.length > 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx(
      "select",
      {
        className: inputClasses,
        style: inputStyle,
        value: String(value),
        onChange: handleChange,
        children: param.options.map((opt) => /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: opt, children: opt }, opt))
      }
    ) : /* @__PURE__ */ jsxRuntimeExports.jsx(
      "input",
      {
        type: param.type === "float" || param.type === "integer" ? "number" : "text",
        className: inputClasses,
        style: inputStyle,
        value: value === null || value === void 0 ? "" : String(value),
        onChange: handleChange,
        min: param.min,
        max: param.max,
        step: param.type === "float" ? "any" : param.type === "integer" ? 1 : void 0,
        placeholder: param.description
      }
    ),
    param.description && /* @__PURE__ */ jsxRuntimeExports.jsx(
      "p",
      {
        className: "text-xs",
        style: { color: "var(--color-text-tertiary)" },
        children: param.description
      }
    )
  ] });
}
const exportOptions = [
  { format: "xlsx", label: "Excel (.xlsx)", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(FileSpreadsheet, { className: "w-4 h-4" }) },
  { format: "pdf", label: "PDF (.pdf)", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(FileText, { className: "w-4 h-4" }) },
  { format: "csv", label: "CSV (.csv)", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(FileSpreadsheet, { className: "w-4 h-4" }) },
  { format: "json", label: "JSON (.json)", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(FileText, { className: "w-4 h-4" }) }
];
function ExportButton({ onExport, isLoading, disabled, size = "sm" }) {
  const [isOpen, setIsOpen] = reactExports.useState(false);
  const dropdownRef = reactExports.useRef(null);
  reactExports.useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);
  const handleExport = (format) => {
    onExport(format);
    setIsOpen(false);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative", ref: dropdownRef, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      Button,
      {
        variant: "secondary",
        size,
        disabled: disabled || isLoading,
        onClick: () => setIsOpen(!isOpen),
        className: "flex items-center gap-2",
        children: [
          isLoading ? /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-4 h-4 animate-spin" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Download, { className: "w-4 h-4" }),
          "Export",
          /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronDown, { className: `w-4 h-4 transition-transform ${isOpen ? "rotate-180" : ""}` })
        ]
      }
    ),
    isOpen && /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "absolute right-0 mt-2 w-48 rounded-lg shadow-lg border z-50",
        style: {
          backgroundColor: "var(--color-bg-elevated)",
          borderColor: "var(--color-border-default)"
        },
        children: /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "py-1", children: exportOptions.map((option) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "button",
          {
            onClick: () => handleExport(option.format),
            className: "w-full flex items-center gap-3 px-4 py-2 text-sm transition-colors",
            style: { color: "var(--color-text-primary)" },
            onMouseEnter: (e) => {
              e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
            },
            onMouseLeave: (e) => {
              e.currentTarget.style.backgroundColor = "transparent";
            },
            children: [
              option.icon,
              option.label
            ]
          },
          option.format
        )) })
      }
    )
  ] });
}
const REPORT_TYPE_INFO = {
  batch_summary: {
    label: "Batch Summary",
    description: "Summary statistics for a specific batch"
  },
  period_stats: {
    label: "Period Statistics",
    description: "Statistics grouped by time period with trend analysis"
  },
  step_analysis: {
    label: "Step Analysis",
    description: "Step-level failure and performance analysis"
  }
};
const reportTypes = ["batch_summary", "period_stats", "step_analysis"];
function ReportTypeSelector({ selectedType, onSelect }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsx(
    "div",
    {
      className: "flex rounded-lg p-1",
      style: { backgroundColor: "var(--color-bg-tertiary)" },
      children: reportTypes.map((type) => {
        const info = REPORT_TYPE_INFO[type];
        const isSelected = selectedType === type;
        return /* @__PURE__ */ jsxRuntimeExports.jsx(
          "button",
          {
            onClick: () => onSelect(type),
            className: `flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${isSelected ? "shadow-sm" : ""}`,
            style: {
              backgroundColor: isSelected ? "var(--color-bg-elevated)" : "transparent",
              color: isSelected ? "var(--color-text-primary)" : "var(--color-text-secondary)"
            },
            title: info.description,
            children: info.label
          },
          type
        );
      })
    }
  );
}
const statusOptions = [
  { value: "", label: "All Status" },
  { value: "completed", label: "Completed" },
  { value: "failed", label: "Failed" },
  { value: "running", label: "Running" },
  { value: "stopped", label: "Stopped" }
];
function ResultsFilter({
  batchId,
  onBatchChange,
  status,
  onStatusChange,
  fromDate,
  onFromDateChange,
  toDate,
  onToDateChange,
  search,
  onSearchChange,
  onClear,
  batches: batches2
}) {
  const batchOptions = [
    { value: "", label: "All Batches" },
    ...batches2.map((b) => ({ value: b.id, label: b.name }))
  ];
  const hasActiveFilters = batchId || status || fromDate || toDate || search;
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
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Filter, { className: "w-4 h-4", style: { color: "var(--color-text-secondary)" } }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: "Filters" })
          ] }),
          hasActiveFilters && /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "ghost", size: "sm", onClick: onClear, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-4 h-4 mr-1" }),
            "Clear"
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Select,
            {
              options: batchOptions,
              value: batchId,
              onChange: (e) => onBatchChange(e.target.value)
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Select,
            {
              options: statusOptions,
              value: status,
              onChange: (e) => onStatusChange(e.target.value)
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Calendar, { className: "w-4 h-4 flex-shrink-0", style: { color: "var(--color-text-secondary)" } }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Input,
              {
                type: "date",
                value: fromDate,
                onChange: (e) => onFromDateChange(e.target.value),
                placeholder: "From"
              }
            )
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Calendar, { className: "w-4 h-4 flex-shrink-0", style: { color: "var(--color-text-secondary)" } }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Input,
              {
                type: "date",
                value: toDate,
                onChange: (e) => onToDateChange(e.target.value),
                placeholder: "To"
              }
            )
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Input,
            {
              placeholder: "Search sequence...",
              value: search,
              onChange: (e) => onSearchChange(e.target.value)
            }
          )
        ] })
      ]
    }
  );
}
const getStatusIcon$1 = (status) => {
  const iconProps = { className: "w-4 h-4" };
  const styles = {
    completed: { color: "var(--color-step-completed-text)" },
    failed: { color: "var(--color-step-failed-text)" },
    running: { color: "var(--color-step-running-text)" },
    stopped: { color: "var(--color-step-pending-text)" }
  };
  switch (status) {
    case "completed":
      return /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { ...iconProps, style: styles.completed });
    case "failed":
      return /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { ...iconProps, style: styles.failed });
    case "running":
      return /* @__PURE__ */ jsxRuntimeExports.jsx(CirclePlay, { ...iconProps, style: styles.running });
    case "stopped":
      return /* @__PURE__ */ jsxRuntimeExports.jsx(CircleStop, { ...iconProps, style: styles.stopped });
  }
};
const statusLabels = {
  completed: "Completed",
  failed: "Failed",
  running: "Running",
  stopped: "Stopped"
};
function formatDuration$4(ms) {
  if (ms < 1e3) return `${ms}ms`;
  if (ms < 6e4) return `${(ms / 1e3).toFixed(1)}s`;
  return `${Math.floor(ms / 6e4)}m ${Math.floor(ms % 6e4 / 1e3)}s`;
}
function formatDateTime$1(date) {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleString("en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
}
function ResultsTable({
  results,
  isLoading,
  selectedIds,
  onSelectionChange,
  onViewDetail,
  sortField,
  sortDirection,
  onSort
}) {
  const [allSelected, setAllSelected] = reactExports.useState(false);
  const handleSelectAll = () => {
    if (allSelected) {
      onSelectionChange([]);
    } else {
      onSelectionChange(results.map((r) => r.id));
    }
    setAllSelected(!allSelected);
  };
  const handleSelectOne = (id) => {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter((i) => i !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };
  const SortIcon = ({ field }) => {
    if (sortField !== field) return null;
    return sortDirection === "asc" ? /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronUp, { className: "w-4 h-4" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronDown, { className: "w-4 h-4" });
  };
  const headerClass = "px-4 py-3 text-left text-xs font-medium uppercase tracking-wider cursor-pointer hover:bg-opacity-50 transition-colors";
  if (isLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-center h-64", children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "lg" }) });
  }
  if (results.length === 0) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "flex items-center justify-center h-64 text-sm",
        style: { color: "var(--color-text-tertiary)" },
        children: "No results found. Adjust your filters or run a sequence."
      }
    );
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "overflow-x-auto rounded-lg border", style: { borderColor: "var(--color-border-default)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsxs("table", { className: "min-w-full divide-y", style: { backgroundColor: "var(--color-bg-secondary)" }, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("thead", { style: { backgroundColor: "var(--color-bg-tertiary)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsxs("tr", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("th", { className: "px-4 py-3 w-12", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
        "input",
        {
          type: "checkbox",
          checked: allSelected,
          onChange: handleSelectAll,
          className: "rounded",
          style: { borderColor: "var(--color-input-border)" }
        }
      ) }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "th",
        {
          className: headerClass,
          style: { color: "var(--color-text-secondary)" },
          onClick: () => onSort("status"),
          children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1", children: [
            "Status ",
            /* @__PURE__ */ jsxRuntimeExports.jsx(SortIcon, { field: "status" })
          ] })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "th",
        {
          className: headerClass,
          style: { color: "var(--color-text-secondary)" },
          onClick: () => onSort("sequenceName"),
          children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1", children: [
            "Sequence ",
            /* @__PURE__ */ jsxRuntimeExports.jsx(SortIcon, { field: "sequenceName" })
          ] })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "th",
        {
          className: headerClass,
          style: { color: "var(--color-text-secondary)" },
          onClick: () => onSort("batchId"),
          children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1", children: [
            "Batch ",
            /* @__PURE__ */ jsxRuntimeExports.jsx(SortIcon, { field: "batchId" })
          ] })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "th",
        {
          className: headerClass,
          style: { color: "var(--color-text-secondary)" },
          onClick: () => onSort("startedAt"),
          children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1", children: [
            "Started At ",
            /* @__PURE__ */ jsxRuntimeExports.jsx(SortIcon, { field: "startedAt" })
          ] })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "th",
        {
          className: headerClass,
          style: { color: "var(--color-text-secondary)" },
          onClick: () => onSort("duration"),
          children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1", children: [
            "Duration ",
            /* @__PURE__ */ jsxRuntimeExports.jsx(SortIcon, { field: "duration" })
          ] })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "th",
        {
          className: headerClass,
          style: { color: "var(--color-text-secondary)" },
          children: "Actions"
        }
      )
    ] }) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("tbody", { className: "divide-y", style: { borderColor: "var(--color-border-subtle)" }, children: results.map((result) => {
      var _a;
      return /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "tr",
        {
          className: "transition-colors",
          style: {
            backgroundColor: selectedIds.includes(result.id) ? "var(--color-bg-tertiary)" : "transparent"
          },
          onMouseEnter: (e) => {
            if (!selectedIds.includes(result.id)) {
              e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
            }
          },
          onMouseLeave: (e) => {
            if (!selectedIds.includes(result.id)) {
              e.currentTarget.style.backgroundColor = "transparent";
            }
          },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
              "input",
              {
                type: "checkbox",
                checked: selectedIds.includes(result.id),
                onChange: () => handleSelectOne(result.id),
                className: "rounded",
                style: { borderColor: "var(--color-input-border)" }
              }
            ) }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
              getStatusIcon$1(result.status),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "span",
                {
                  className: "text-sm font-medium",
                  style: { color: "var(--color-text-primary)" },
                  children: statusLabels[result.status]
                }
              )
            ] }) }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("td", { className: "px-4 py-3", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-text-primary)" }, children: result.sequenceName }),
              result.sequenceVersion && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "span",
                {
                  className: "ml-2 text-xs px-1.5 py-0.5 rounded",
                  style: {
                    backgroundColor: "var(--color-bg-tertiary)",
                    color: "var(--color-text-secondary)"
                  },
                  children: [
                    "v",
                    result.sequenceVersion
                  ]
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-mono", style: { color: "var(--color-text-secondary)" }, children: ((_a = result.batchId) == null ? void 0 : _a.slice(0, 8)) ?? "-" }) }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: result.startedAt ? formatDateTime$1(result.startedAt) : "-" }) }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-mono", style: { color: "var(--color-text-secondary)" }, children: result.duration ? formatDuration$4(result.duration) : "-" }) }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: () => onViewDetail(result), children: /* @__PURE__ */ jsxRuntimeExports.jsx(Eye, { className: "w-4 h-4" }) }) })
          ]
        },
        result.id
      );
    }) })
  ] }) });
}
const getStatusIcon = (status) => {
  const iconProps = { className: "w-5 h-5" };
  const styles = {
    completed: { color: "var(--color-step-completed-text)" },
    failed: { color: "var(--color-step-failed-text)" },
    running: { color: "var(--color-step-running-text)" },
    stopped: { color: "var(--color-step-pending-text)" }
  };
  switch (status) {
    case "completed":
      return /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheckBig, { ...iconProps, style: styles.completed });
    case "failed":
      return /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { ...iconProps, style: styles.failed });
    case "running":
      return /* @__PURE__ */ jsxRuntimeExports.jsx(CirclePlay, { ...iconProps, style: styles.running });
    case "stopped":
      return /* @__PURE__ */ jsxRuntimeExports.jsx(CircleStop, { ...iconProps, style: styles.stopped });
  }
};
const getStepStatusStyles = (status) => {
  const styles = {
    pending: { backgroundColor: "var(--color-step-pending-bg)", color: "var(--color-step-pending-text)" },
    running: { backgroundColor: "var(--color-step-running-bg)", color: "var(--color-step-running-text)" },
    completed: { backgroundColor: "var(--color-step-completed-bg)", color: "var(--color-step-completed-text)" },
    failed: { backgroundColor: "var(--color-step-failed-bg)", color: "var(--color-step-failed-text)" },
    skipped: { backgroundColor: "var(--color-step-skipped-bg)", color: "var(--color-step-skipped-text)" }
  };
  return styles[status];
};
function formatDuration$3(ms) {
  if (ms < 1e3) return `${ms}ms`;
  if (ms < 6e4) return `${(ms / 1e3).toFixed(2)}s`;
  return `${Math.floor(ms / 6e4)}m ${(ms % 6e4 / 1e3).toFixed(1)}s`;
}
function formatDateTime(date) {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleString("en-US");
}
function StepRow$1({ step, index }) {
  const [expanded, setExpanded] = reactExports.useState(false);
  const hasDetails = step.result || step.error;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "border-b last:border-b-0",
      style: { borderColor: "var(--color-border-subtle)" },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: `flex items-center gap-3 px-4 py-3 ${hasDetails ? "cursor-pointer" : ""}`,
            onClick: () => hasDetails && setExpanded(!expanded),
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "span",
                {
                  className: "w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium",
                  style: { backgroundColor: "var(--color-bg-tertiary)", color: "var(--color-text-secondary)" },
                  children: step.order || index + 1
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex-1 min-w-0", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: step.name }),
                step.status && /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "span",
                  {
                    className: "px-2 py-0.5 rounded text-xs font-medium",
                    style: getStepStatusStyles(step.status),
                    children: step.status
                  }
                )
              ] }) }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-mono", style: { color: "var(--color-text-secondary)" }, children: step.duration ? formatDuration$3(step.duration * 1e3) : "-" }),
              hasDetails && (expanded ? /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronDown, { className: "w-4 h-4", style: { color: "var(--color-text-tertiary)" } }) : /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronRight, { className: "w-4 h-4", style: { color: "var(--color-text-tertiary)" } }))
            ]
          }
        ),
        expanded && hasDetails && /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "px-4 pb-3 ml-9",
            style: { backgroundColor: "var(--color-bg-tertiary)" },
            children: [
              step.error && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-2", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs font-medium", style: { color: "var(--color-step-failed-text)" }, children: "Error:" }),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "pre",
                  {
                    className: "mt-1 text-xs p-2 rounded overflow-x-auto",
                    style: { backgroundColor: "var(--color-bg-elevated)", color: "var(--color-text-secondary)" },
                    children: step.error
                  }
                )
              ] }),
              step.result && Object.keys(step.result).length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs font-medium", style: { color: "var(--color-text-secondary)" }, children: "Result Data:" }),
                /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "mt-1 grid grid-cols-2 gap-2", children: Object.entries(step.result).map(([key, value]) => /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex justify-between text-xs", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { style: { color: "var(--color-text-tertiary)" }, children: [
                    key,
                    ":"
                  ] }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-mono", style: { color: "var(--color-text-primary)" }, children: typeof value === "number" ? value.toFixed(3) : String(value) })
                ] }, key)) })
              ] })
            ]
          }
        )
      ]
    }
  );
}
function ResultDetailModal({ result, onClose }) {
  var _a, _b;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "fixed inset-0 z-50 flex items-center justify-center", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "absolute inset-0 bg-black/50",
        onClick: onClose
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "relative w-full max-w-2xl max-h-[90vh] overflow-hidden rounded-xl shadow-xl",
        style: { backgroundColor: "var(--color-bg-elevated)" },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "div",
            {
              className: "flex items-center justify-between px-6 py-4 border-b",
              style: { borderColor: "var(--color-border-default)" },
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
                  getStatusIcon(result.status),
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: result.sequenceName }),
                    /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: [
                      result.sequenceVersion && `v${result.sequenceVersion} · `,
                      result.id.slice(0, 8)
                    ] })
                  ] })
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: onClose, children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-5 h-5" }) })
              ]
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "overflow-y-auto max-h-[calc(90vh-140px)]", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "div",
              {
                className: "grid grid-cols-2 md:grid-cols-4 gap-4 p-6 border-b",
                style: { borderColor: "var(--color-border-default)" },
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Batch" }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm font-mono", style: { color: "var(--color-text-primary)" }, children: ((_a = result.batchId) == null ? void 0 : _a.slice(0, 8)) ?? "-" })
                  ] }),
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Started At" }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-primary)" }, children: result.startedAt ? formatDateTime(result.startedAt) : "-" })
                  ] }),
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Completed At" }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", style: { color: "var(--color-text-primary)" }, children: result.completedAt ? formatDateTime(result.completedAt) : "-" })
                  ] }),
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Duration" }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm font-mono", style: { color: "var(--color-text-primary)" }, children: result.duration ? formatDuration$3(result.duration) : "-" })
                  ] })
                ]
              }
            ),
            !result.overallPass && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "px-6 py-4 border-b", style: { borderColor: "var(--color-border-default)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "div",
              {
                className: "flex items-center gap-2",
                style: { color: "var(--color-step-failed-text)" },
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(CircleX, { className: "w-4 h-4" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", children: "Execution failed - check step details below" })
                ]
              }
            ) }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "px-6 py-4", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("h4", { className: "text-sm font-medium mb-3", style: { color: "var(--color-text-primary)" }, children: [
                "Steps (",
                ((_b = result.steps) == null ? void 0 : _b.length) ?? 0,
                ")"
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "div",
                {
                  className: "rounded-lg border overflow-hidden",
                  style: { borderColor: "var(--color-border-default)" },
                  children: result.steps && result.steps.length > 0 ? result.steps.map((step, index) => /* @__PURE__ */ jsxRuntimeExports.jsx(StepRow$1, { step, index }, `${step.name}-${step.order}`)) : /* @__PURE__ */ jsxRuntimeExports.jsx(
                    "div",
                    {
                      className: "py-8 text-center text-sm",
                      style: { color: "var(--color-text-tertiary)" },
                      children: "No step data available"
                    }
                  )
                }
              )
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "div",
            {
              className: "flex justify-end px-6 py-4 border-t",
              style: { borderColor: "var(--color-border-default)" },
              children: /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "secondary", onClick: onClose, children: "Close" })
            }
          )
        ]
      }
    )
  ] });
}
function formatDuration$2(ms) {
  if (ms < 1e3) return `${ms.toFixed(0)}ms`;
  if (ms < 6e4) return `${(ms / 1e3).toFixed(2)}s`;
  return `${Math.floor(ms / 6e4)}m ${(ms % 6e4 / 1e3).toFixed(1)}s`;
}
function formatPercent$2(value) {
  return `${(value * 100).toFixed(1)}%`;
}
function getPassRateColor$1(rate) {
  if (rate >= 0.9) return "var(--color-rate-high)";
  if (rate >= 0.7) return "var(--color-rate-medium)";
  return "var(--color-rate-low)";
}
function BatchSummaryReport({ batchId, batchName }) {
  const { data: report, isLoading, error } = useBatchSummaryReport(batchId, batchName);
  const exportMutation = useExportBatchSummaryReport();
  const handleExport = (format) => {
    if (!batchId) return;
    exportMutation.mutate({ batchId, format, batchName });
  };
  if (!batchId) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "flex items-center justify-center h-64 text-sm",
        style: { color: "var(--color-text-tertiary)" },
        children: "Select a batch to view summary report"
      }
    );
  }
  if (isLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-center h-64", children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "lg" }) });
  }
  if (error) {
    return /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "flex items-center justify-center h-64 text-sm",
        style: { color: "var(--color-rate-low)" },
        children: [
          "Failed to load report: ",
          error.message
        ]
      }
    );
  }
  if (!report) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "flex items-center justify-center h-64 text-sm",
        style: { color: "var(--color-text-tertiary)" },
        children: "No data available for this batch"
      }
    );
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: report.batchName || report.batchId }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: [
          report.sequenceName,
          " v",
          report.sequenceVersion
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        ExportButton,
        {
          onExport: handleExport,
          isLoading: exportMutation.isPending
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-2 md:grid-cols-4 gap-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "p-4 rounded-lg",
          style: { backgroundColor: "var(--color-bg-tertiary)" },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Total Executions" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: report.totalExecutions })
          ]
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "p-4 rounded-lg",
          style: { backgroundColor: "var(--color-bg-tertiary)" },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Pass Rate" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "p",
              {
                className: "text-2xl font-bold",
                style: { color: getPassRateColor$1(report.passRate) },
                children: formatPercent$2(report.passRate)
              }
            )
          ]
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "p-4 rounded-lg",
          style: { backgroundColor: "var(--color-bg-tertiary)" },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Pass / Fail" }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-2xl font-bold", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-rate-high)" }, children: report.passCount }),
              " / ",
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-rate-low)" }, children: report.failCount })
            ] })
          ]
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "p-4 rounded-lg",
          style: { backgroundColor: "var(--color-bg-tertiary)" },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Avg Duration" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-2xl font-bold font-mono", style: { color: "var(--color-text-primary)" }, children: formatDuration$2(report.avgDuration) })
          ]
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "text-sm font-medium mb-3", style: { color: "var(--color-text-primary)" }, children: "Step Statistics" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "div",
        {
          className: "rounded-lg border overflow-hidden",
          style: { borderColor: "var(--color-border-default)" },
          children: /* @__PURE__ */ jsxRuntimeExports.jsxs("table", { className: "min-w-full", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("thead", { style: { backgroundColor: "var(--color-bg-tertiary)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsxs("tr", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "th",
                {
                  className: "px-4 py-3 text-left text-xs font-medium uppercase",
                  style: { color: "var(--color-text-secondary)" },
                  children: "Step Name"
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "th",
                {
                  className: "px-4 py-3 text-right text-xs font-medium uppercase",
                  style: { color: "var(--color-text-secondary)" },
                  children: "Runs"
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "th",
                {
                  className: "px-4 py-3 text-right text-xs font-medium uppercase",
                  style: { color: "var(--color-text-secondary)" },
                  children: "Pass Rate"
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "th",
                {
                  className: "px-4 py-3 text-right text-xs font-medium uppercase",
                  style: { color: "var(--color-text-secondary)" },
                  children: "Avg"
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "th",
                {
                  className: "px-4 py-3 text-right text-xs font-medium uppercase",
                  style: { color: "var(--color-text-secondary)" },
                  children: "Min"
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "th",
                {
                  className: "px-4 py-3 text-right text-xs font-medium uppercase",
                  style: { color: "var(--color-text-secondary)" },
                  children: "Max"
                }
              )
            ] }) }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "tbody",
              {
                className: "divide-y",
                style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-subtle)" },
                children: report.steps.map((step) => /* @__PURE__ */ jsxRuntimeExports.jsxs("tr", { children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: step.stepName }) }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3 text-right", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: step.totalRuns }) }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3 text-right", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
                    "span",
                    {
                      className: "text-sm font-medium",
                      style: { color: getPassRateColor$1(step.passRate) },
                      children: formatPercent$2(step.passRate)
                    }
                  ) }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3 text-right", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-mono", style: { color: "var(--color-text-secondary)" }, children: formatDuration$2(step.avgDuration) }) }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3 text-right", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-mono", style: { color: "var(--color-text-secondary)" }, children: formatDuration$2(step.minDuration) }) }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3 text-right", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-mono", style: { color: "var(--color-text-secondary)" }, children: formatDuration$2(step.maxDuration) }) })
                ] }, step.stepName))
              }
            )
          ] })
        }
      )
    ] }),
    (report.firstExecution || report.lastExecution) && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: [
      "Data range:",
      " ",
      report.firstExecution && new Date(report.firstExecution).toLocaleDateString("en-US"),
      " ~ ",
      report.lastExecution && new Date(report.lastExecution).toLocaleDateString("en-US")
    ] })
  ] });
}
const periodOptions = [
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "monthly", label: "Monthly" }
];
function formatPercent$1(value) {
  return `${(value * 100).toFixed(1)}%`;
}
function formatDuration$1(ms) {
  if (ms < 1e3) return `${ms.toFixed(0)}ms`;
  if (ms < 6e4) return `${(ms / 1e3).toFixed(2)}s`;
  return `${Math.floor(ms / 6e4)}m ${(ms % 6e4 / 1e3).toFixed(1)}s`;
}
function getDefaultDates() {
  const to = /* @__PURE__ */ new Date();
  const from = /* @__PURE__ */ new Date();
  from.setDate(from.getDate() - 30);
  return {
    from: from.toISOString().slice(0, 10),
    to: to.toISOString().slice(0, 10)
  };
}
function getPassRateColor(rate) {
  if (rate >= 0.9) return "var(--color-rate-high)";
  if (rate >= 0.7) return "var(--color-rate-medium)";
  return "var(--color-rate-low)";
}
function getTrendColor(direction) {
  if (direction === "increasing") return "var(--color-rate-high)";
  if (direction === "decreasing") return "var(--color-rate-low)";
  return "var(--color-text-secondary)";
}
function PeriodStatsReport({ batchId }) {
  const defaults2 = getDefaultDates();
  const [periodType, setPeriodType] = reactExports.useState("daily");
  const [fromDate, setFromDate] = reactExports.useState(defaults2.from);
  const [toDate, setToDate] = reactExports.useState(defaults2.to);
  const { data: report, isLoading, error } = usePeriodStatsReport(
    periodType,
    fromDate,
    toDate,
    batchId
  );
  const exportMutation = useExportPeriodStatsReport();
  const handleExport = (format) => {
    exportMutation.mutate({ periodType, fromDate, toDate, format, batchId });
  };
  const TrendIcon = () => {
    if (!report) return null;
    const trendColor = getTrendColor(report.trendDirection);
    switch (report.trendDirection) {
      case "increasing":
        return /* @__PURE__ */ jsxRuntimeExports.jsx(TrendingUp, { className: "w-5 h-5", style: { color: trendColor } });
      case "decreasing":
        return /* @__PURE__ */ jsxRuntimeExports.jsx(TrendingDown, { className: "w-5 h-5", style: { color: trendColor } });
      default:
        return /* @__PURE__ */ jsxRuntimeExports.jsx(Minus, { className: "w-5 h-5", style: { color: trendColor } });
    }
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-wrap items-end gap-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "w-40", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("label", { className: "block text-xs mb-1", style: { color: "var(--color-text-tertiary)" }, children: "Period" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Select,
          {
            options: periodOptions,
            value: periodType,
            onChange: (e) => setPeriodType(e.target.value)
          }
        )
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Calendar, { className: "w-4 h-4", style: { color: "var(--color-text-secondary)" } }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("label", { className: "block text-xs mb-1", style: { color: "var(--color-text-tertiary)" }, children: "From" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Input,
            {
              type: "date",
              value: fromDate,
              onChange: (e) => setFromDate(e.target.value)
            }
          )
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("label", { className: "block text-xs mb-1", style: { color: "var(--color-text-tertiary)" }, children: "To" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Input,
          {
            type: "date",
            value: toDate,
            onChange: (e) => setToDate(e.target.value)
          }
        )
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        ExportButton,
        {
          onExport: handleExport,
          isLoading: exportMutation.isPending,
          disabled: !fromDate || !toDate
        }
      )
    ] }),
    isLoading ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-center h-64", children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "lg" }) }) : error ? /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "flex items-center justify-center h-64 text-sm",
        style: { color: "var(--color-rate-low)" },
        children: [
          "Failed to load report: ",
          error.message
        ]
      }
    ) : !report ? /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "flex items-center justify-center h-64 text-sm",
        style: { color: "var(--color-text-tertiary)" },
        children: "No data available for the selected period"
      }
    ) : /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-2 md:grid-cols-4 gap-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "p-4 rounded-lg",
            style: { backgroundColor: "var(--color-bg-tertiary)" },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Total Executions" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: report.totalExecutions })
            ]
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "p-4 rounded-lg",
            style: { backgroundColor: "var(--color-bg-tertiary)" },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Overall Pass Rate" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "p",
                {
                  className: "text-2xl font-bold",
                  style: { color: getPassRateColor(report.overallPassRate) },
                  children: formatPercent$1(report.overallPassRate)
                }
              )
            ]
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "p-4 rounded-lg",
            style: { backgroundColor: "var(--color-bg-tertiary)" },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Periods" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: report.dataPoints.length })
            ]
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "p-4 rounded-lg",
            style: { backgroundColor: "var(--color-bg-tertiary)" },
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Trend" }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mt-1", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(TrendIcon, {}),
                /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  "span",
                  {
                    className: "text-xl font-bold",
                    style: { color: getTrendColor(report.trendDirection) },
                    children: [
                      report.trendPercentage > 0 ? "+" : "",
                      formatPercent$1(report.trendPercentage / 100)
                    ]
                  }
                )
              ] })
            ]
          }
        )
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h4", { className: "text-sm font-medium mb-3", style: { color: "var(--color-text-primary)" }, children: "Period Breakdown" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "div",
          {
            className: "rounded-lg border overflow-hidden",
            style: { borderColor: "var(--color-border-default)" },
            children: /* @__PURE__ */ jsxRuntimeExports.jsxs("table", { className: "min-w-full", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("thead", { style: { backgroundColor: "var(--color-bg-tertiary)" }, children: /* @__PURE__ */ jsxRuntimeExports.jsxs("tr", { children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "th",
                  {
                    className: "px-4 py-3 text-left text-xs font-medium uppercase",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Period"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "th",
                  {
                    className: "px-4 py-3 text-right text-xs font-medium uppercase",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Total"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "th",
                  {
                    className: "px-4 py-3 text-right text-xs font-medium uppercase",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Pass"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "th",
                  {
                    className: "px-4 py-3 text-right text-xs font-medium uppercase",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Fail"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "th",
                  {
                    className: "px-4 py-3 text-right text-xs font-medium uppercase",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Pass Rate"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "th",
                  {
                    className: "px-4 py-3 text-right text-xs font-medium uppercase",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Avg Duration"
                  }
                )
              ] }) }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "tbody",
                {
                  className: "divide-y",
                  style: { backgroundColor: "var(--color-bg-secondary)", borderColor: "var(--color-border-subtle)" },
                  children: report.dataPoints.map((point) => /* @__PURE__ */ jsxRuntimeExports.jsxs("tr", { children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: point.periodLabel }) }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3 text-right", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: point.total }) }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3 text-right", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-rate-high)" }, children: point.passCount }) }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3 text-right", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", style: { color: "var(--color-rate-low)" }, children: point.failCount }) }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3 text-right", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
                      "span",
                      {
                        className: "text-sm font-medium",
                        style: { color: getPassRateColor(point.passRate) },
                        children: formatPercent$1(point.passRate)
                      }
                    ) }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("td", { className: "px-4 py-3 text-right", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-mono", style: { color: "var(--color-text-secondary)" }, children: formatDuration$1(point.avgDuration) }) })
                  ] }, point.periodLabel))
                }
              )
            ] })
          }
        )
      ] })
    ] })
  ] });
}
function formatPercent(value) {
  return `${(value * 100).toFixed(1)}%`;
}
function formatDuration(ms) {
  if (ms < 1e3) return `${ms.toFixed(0)}ms`;
  if (ms < 6e4) return `${(ms / 1e3).toFixed(2)}s`;
  return `${Math.floor(ms / 6e4)}m ${(ms % 6e4 / 1e3).toFixed(1)}s`;
}
function getFailRateColor(rate) {
  if (rate > 0.1) return "var(--color-rate-low)";
  if (rate > 0.05) return "var(--color-rate-medium)";
  return "var(--color-text-secondary)";
}
function StepRow({ step, isMostFailed, isSlowest }) {
  const [expanded, setExpanded] = reactExports.useState(false);
  const hasFailures = step.failureReasons && step.failureReasons.length > 0;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    "div",
    {
      className: "border-b last:border-b-0",
      style: { borderColor: "var(--color-border-subtle)" },
      children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: `flex items-center gap-3 px-4 py-3 ${hasFailures ? "cursor-pointer" : ""}`,
            onClick: () => hasFailures && setExpanded(!expanded),
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex-1 min-w-0", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: step.stepName }),
                isMostFailed && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  "span",
                  {
                    className: "flex items-center gap-1 px-2 py-0.5 rounded text-xs",
                    style: { backgroundColor: "var(--color-step-failed-bg)", color: "var(--color-step-failed-text)" },
                    children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-3 h-3" }),
                      "Most Failed"
                    ]
                  }
                ),
                isSlowest && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  "span",
                  {
                    className: "flex items-center gap-1 px-2 py-0.5 rounded text-xs",
                    style: { backgroundColor: "var(--color-step-skipped-bg)", color: "var(--color-step-skipped-text)" },
                    children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-3 h-3" }),
                      "Slowest"
                    ]
                  }
                )
              ] }) }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-6 text-sm", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "text-right w-16", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: step.totalRuns }) }),
                /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "text-right w-20", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: getFailRateColor(step.failRate) }, children: formatPercent(step.failRate) }) }),
                /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "text-right w-24 font-mono", style: { color: "var(--color-text-secondary)" }, children: formatDuration(step.avgDuration) }),
                /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "text-right w-24 font-mono", style: { color: "var(--color-text-secondary)" }, children: formatDuration(step.p95Duration) })
              ] }),
              hasFailures && (expanded ? /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronDown, { className: "w-4 h-4", style: { color: "var(--color-text-tertiary)" } }) : /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronRight, { className: "w-4 h-4", style: { color: "var(--color-text-tertiary)" } }))
            ]
          }
        ),
        expanded && hasFailures && /* @__PURE__ */ jsxRuntimeExports.jsx(
          "div",
          {
            className: "px-4 pb-4",
            style: { backgroundColor: "var(--color-bg-tertiary)" },
            children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "ml-4", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("h5", { className: "text-xs font-medium mb-2", style: { color: "var(--color-text-secondary)" }, children: "Failure Reasons" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-2", children: step.failureReasons.map((reason, index) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "div",
                {
                  className: "flex items-start gap-3 p-2 rounded",
                  style: { backgroundColor: "var(--color-bg-elevated)" },
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsxs(
                      "div",
                      {
                        className: "flex-shrink-0 px-2 py-0.5 rounded text-xs font-medium",
                        style: { backgroundColor: "var(--color-bg-tertiary)", color: "var(--color-text-secondary)" },
                        children: [
                          reason.occurrenceCount,
                          "x"
                        ]
                      }
                    ),
                    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 min-w-0", children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs", style: { color: "var(--color-text-primary)" }, children: reason.errorMessage }),
                      /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs mt-1", style: { color: "var(--color-text-tertiary)" }, children: [
                        formatPercent(reason.percentage),
                        " of failures"
                      ] })
                    ] })
                  ]
                },
                index
              )) })
            ] })
          }
        )
      ]
    }
  );
}
function StepAnalysisReport({ batchId }) {
  const filters = batchId ? { batchId } : {};
  const { data: report, isLoading, error } = useStepAnalysisReport(filters);
  const exportMutation = useExportStepAnalysisReport();
  const handleExport = (format) => {
    exportMutation.mutate({ format, filters });
  };
  if (isLoading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-center h-64", children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoadingSpinner, { size: "lg" }) });
  }
  if (error) {
    return /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "flex items-center justify-center h-64 text-sm",
        style: { color: "var(--color-rate-low)" },
        children: [
          "Failed to load report: ",
          error.message
        ]
      }
    );
  }
  if (!report || report.steps.length === 0) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(
      "div",
      {
        className: "flex items-center justify-center h-64 text-sm",
        style: { color: "var(--color-text-tertiary)" },
        children: "No step data available for analysis"
      }
    );
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-lg font-semibold", style: { color: "var(--color-text-primary)" }, children: "Step Analysis" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm", style: { color: "var(--color-text-secondary)" }, children: [
          report.totalSteps,
          " steps analyzed"
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        ExportButton,
        {
          onExport: handleExport,
          isLoading: exportMutation.isPending
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-2 gap-4", children: [
      report.mostFailedStep && /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "p-4 rounded-lg border-l-4",
          style: { backgroundColor: "var(--color-bg-tertiary)", borderColor: "var(--color-step-failed-text)" },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mb-1", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "w-4 h-4", style: { color: "var(--color-step-failed-text)" } }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Most Failed Step" })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: report.mostFailedStep })
          ]
        }
      ),
      report.slowestStep && /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "p-4 rounded-lg border-l-4",
          style: { backgroundColor: "var(--color-bg-tertiary)", borderColor: "var(--color-step-skipped-text)" },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mb-1", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-4 h-4", style: { color: "var(--color-step-skipped-text)" } }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: "Slowest Step" })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm font-medium", style: { color: "var(--color-text-primary)" }, children: report.slowestStep })
          ]
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "flex items-center gap-3 px-4 py-2 text-xs font-medium uppercase",
          style: { backgroundColor: "var(--color-bg-tertiary)", color: "var(--color-text-secondary)" },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex-1", children: "Step Name" }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-6", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-16 text-right", children: "Runs" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-20 text-right", children: "Fail Rate" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-24 text-right", children: "Avg" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-24 text-right", children: "P95" })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-4" })
          ]
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        "div",
        {
          className: "rounded-lg border overflow-hidden",
          style: { borderColor: "var(--color-border-default)" },
          children: report.steps.map((step) => /* @__PURE__ */ jsxRuntimeExports.jsx(
            StepRow,
            {
              step,
              isMostFailed: step.stepName === report.mostFailedStep,
              isSlowest: step.stepName === report.slowestStep
            },
            step.stepName
          ))
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "text-xs", style: { color: "var(--color-text-tertiary)" }, children: [
      "Report generated at: ",
      new Date(report.reportGeneratedAt).toLocaleString("en-US")
    ] })
  ] });
}
function ResultsPage() {
  var _a;
  const [viewMode, setViewMode] = reactExports.useState("list");
  const [batchFilter, setBatchFilter] = reactExports.useState("");
  const [statusFilter, setStatusFilter] = reactExports.useState("");
  const [fromDate, setFromDate] = reactExports.useState("");
  const [toDate, setToDate] = reactExports.useState("");
  const [searchFilter, setSearchFilter] = reactExports.useState("");
  const [sortField, setSortField] = reactExports.useState("startedAt");
  const [sortDirection, setSortDirection] = reactExports.useState("desc");
  const [selectedIds, setSelectedIds] = reactExports.useState([]);
  const [selectedResult, setSelectedResult] = reactExports.useState(null);
  const [detailResultId, setDetailResultId] = reactExports.useState(null);
  const [reportType, setReportType] = reactExports.useState("batch_summary");
  const [reportBatchId, setReportBatchId] = reactExports.useState(null);
  const { data: batches2 } = useBatchList();
  const { data: resultsData, isLoading: resultsLoading } = useResultList(
    {
      batchId: batchFilter || void 0,
      status: statusFilter === "completed" || statusFilter === "failed" ? statusFilter : void 0,
      from: fromDate || void 0,
      to: toDate || void 0
    }
  );
  const { data: detailResult } = useResult(detailResultId ?? "");
  const bulkExportMutation = useExportResultsBulk();
  const handleClearFilters = reactExports.useCallback(() => {
    setBatchFilter("");
    setStatusFilter("");
    setFromDate("");
    setToDate("");
    setSearchFilter("");
  }, []);
  const handleSort = reactExports.useCallback((field) => {
    if (sortField === field) {
      setSortDirection((prev) => prev === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  }, [sortField]);
  const handleViewDetail = reactExports.useCallback((result) => {
    setSelectedResult(result);
    setDetailResultId(result.id);
  }, []);
  const handleCloseDetail = reactExports.useCallback(() => {
    setSelectedResult(null);
    setDetailResultId(null);
  }, []);
  const handleBulkExport = reactExports.useCallback((format) => {
    if (selectedIds.length === 0) return;
    bulkExportMutation.mutate({
      resultIds: selectedIds,
      format,
      includeStepDetails: true
    });
  }, [selectedIds, bulkExportMutation]);
  const filteredResults = ((resultsData == null ? void 0 : resultsData.items) ?? []).filter((result) => {
    if (searchFilter) {
      return result.sequenceName.toLowerCase().includes(searchFilter.toLowerCase());
    }
    return true;
  }).sort((a, b) => {
    let aVal = "";
    let bVal = "";
    switch (sortField) {
      case "status":
        aVal = a.status;
        bVal = b.status;
        break;
      case "sequenceName":
        aVal = a.sequenceName;
        bVal = b.sequenceName;
        break;
      case "batchId":
        aVal = a.batchId || "";
        bVal = b.batchId || "";
        break;
      case "startedAt":
        aVal = new Date(a.startedAt).getTime();
        bVal = new Date(b.startedAt).getTime();
        break;
      case "duration":
        aVal = a.duration ?? 0;
        bVal = b.duration ?? 0;
        break;
    }
    if (typeof aVal === "string" && typeof bVal === "string") {
      return sortDirection === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    }
    return sortDirection === "asc" ? Number(aVal) - Number(bVal) : Number(bVal) - Number(aVal);
  });
  const batchOptions = [
    { value: "", label: "Select a batch..." },
    ...(batches2 == null ? void 0 : batches2.map((b) => ({ value: b.id, label: b.name }))) ?? []
  ];
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(ClipboardList, { className: "w-6 h-6 text-brand-500" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-2xl font-bold", style: { color: "var(--color-text-primary)" }, children: "Results" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "flex rounded-lg p-1",
          style: { backgroundColor: "var(--color-bg-tertiary)" },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "button",
              {
                onClick: () => setViewMode("list"),
                className: `flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${viewMode === "list" ? "shadow-sm" : ""}`,
                style: {
                  backgroundColor: viewMode === "list" ? "var(--color-bg-elevated)" : "transparent",
                  color: viewMode === "list" ? "var(--color-text-primary)" : "var(--color-text-secondary)"
                },
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(List, { className: "w-4 h-4" }),
                  "List"
                ]
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "button",
              {
                onClick: () => setViewMode("reports"),
                className: `flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${viewMode === "reports" ? "shadow-sm" : ""}`,
                style: {
                  backgroundColor: viewMode === "reports" ? "var(--color-bg-elevated)" : "transparent",
                  color: viewMode === "reports" ? "var(--color-text-primary)" : "var(--color-text-secondary)"
                },
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(ChartNoAxesColumn, { className: "w-4 h-4" }),
                  "Reports"
                ]
              }
            )
          ]
        }
      )
    ] }),
    viewMode === "list" ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        ResultsFilter,
        {
          batchId: batchFilter,
          onBatchChange: setBatchFilter,
          status: statusFilter,
          onStatusChange: setStatusFilter,
          fromDate,
          onFromDateChange: setFromDate,
          toDate,
          onToDateChange: setToDate,
          search: searchFilter,
          onSearchChange: setSearchFilter,
          onClear: handleClearFilters,
          batches: (batches2 == null ? void 0 : batches2.map((b) => ({ id: b.id, name: b.name }))) ?? []
        }
      ),
      selectedIds.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "flex items-center justify-between p-3 rounded-lg",
          style: { backgroundColor: "var(--color-bg-tertiary)" },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-sm", style: { color: "var(--color-text-primary)" }, children: [
              selectedIds.length,
              " result(s) selected"
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              ExportButton,
              {
                onExport: handleBulkExport,
                isLoading: bulkExportMutation.isPending
              }
            )
          ]
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        ResultsTable,
        {
          results: filteredResults,
          isLoading: resultsLoading,
          selectedIds,
          onSelectionChange: setSelectedIds,
          onViewDetail: handleViewDetail,
          sortField,
          sortDirection,
          onSort: handleSort
        }
      ),
      resultsData && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "text-sm", style: { color: "var(--color-text-tertiary)" }, children: [
        "Showing ",
        filteredResults.length,
        " of ",
        resultsData.total,
        " results"
      ] })
    ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        ReportTypeSelector,
        {
          selectedType: reportType,
          onSelect: setReportType
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "p-6 rounded-lg border",
          style: {
            backgroundColor: "var(--color-bg-secondary)",
            borderColor: "var(--color-border-default)"
          },
          children: [
            reportType === "batch_summary" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "max-w-xs", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("label", { className: "block text-xs mb-1", style: { color: "var(--color-text-tertiary)" }, children: "Select Batch" }),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  Select,
                  {
                    options: batchOptions,
                    value: reportBatchId ?? "",
                    onChange: (e) => setReportBatchId(e.target.value || null)
                  }
                )
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                BatchSummaryReport,
                {
                  batchId: reportBatchId,
                  batchName: (_a = batches2 == null ? void 0 : batches2.find((b) => b.id === reportBatchId)) == null ? void 0 : _a.name
                }
              )
            ] }),
            reportType === "period_stats" && /* @__PURE__ */ jsxRuntimeExports.jsx(PeriodStatsReport, { batchId: reportBatchId ?? void 0 }),
            reportType === "step_analysis" && /* @__PURE__ */ jsxRuntimeExports.jsx(StepAnalysisReport, { batchId: reportBatchId ?? void 0 })
          ]
        }
      )
    ] }),
    selectedResult && detailResult && /* @__PURE__ */ jsxRuntimeExports.jsx(
      ResultDetailModal,
      {
        result: detailResult,
        onClose: handleCloseDetail
      }
    )
  ] });
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
  var _a;
  const { data: systemInfo, isLoading: infoLoading, refetch: refetchInfo } = useSystemInfo();
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useHealthStatus();
  const { data: workflowConfig, isLoading: workflowLoading, refetch: refetchWorkflow } = useWorkflowConfig();
  const { data: backendConfig, isLoading: backendLoading, refetch: refetchBackend } = useBackendConfig();
  const updateStationInfo2 = useUpdateStationInfo();
  const updateWorkflow = useUpdateWorkflowConfig();
  const updateBackend = useUpdateBackendConfig();
  const addNotification = useNotificationStore((state) => state.addNotification);
  const theme = useUIStore((state) => state.theme);
  const toggleTheme = useUIStore((state) => state.toggleTheme);
  const [isEditing, setIsEditing] = reactExports.useState(false);
  const [editForm, setEditForm] = reactExports.useState({
    id: "",
    name: "",
    description: ""
  });
  const [isEditingBackend, setIsEditingBackend] = reactExports.useState(false);
  const [backendForm, setBackendForm] = reactExports.useState({
    url: "",
    syncInterval: 30,
    stationId: "",
    timeout: 30,
    maxRetries: 5
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
  reactExports.useEffect(() => {
    if (backendConfig && !isEditingBackend) {
      setBackendForm({
        url: backendConfig.url,
        syncInterval: backendConfig.syncInterval,
        stationId: backendConfig.stationId,
        timeout: backendConfig.timeout,
        maxRetries: backendConfig.maxRetries
      });
    }
  }, [backendConfig, isEditingBackend]);
  const handleRefresh = () => {
    refetchInfo();
    refetchHealth();
    refetchWorkflow();
    refetchBackend();
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
  const handleBackendEditStart = () => {
    if (backendConfig) {
      setBackendForm({
        url: backendConfig.url,
        syncInterval: backendConfig.syncInterval,
        stationId: backendConfig.stationId,
        timeout: backendConfig.timeout,
        maxRetries: backendConfig.maxRetries
      });
    }
    setIsEditingBackend(true);
  };
  const handleBackendEditCancel = () => {
    setIsEditingBackend(false);
    if (backendConfig) {
      setBackendForm({
        url: backendConfig.url,
        syncInterval: backendConfig.syncInterval,
        stationId: backendConfig.stationId,
        timeout: backendConfig.timeout,
        maxRetries: backendConfig.maxRetries
      });
    }
  };
  const handleBackendEditSave = async () => {
    if (!backendForm.url.trim()) {
      addNotification({
        type: "error",
        title: "Validation Error",
        message: "Backend URL is required"
      });
      return;
    }
    try {
      await updateBackend.mutateAsync({
        url: backendForm.url.trim(),
        syncInterval: backendForm.syncInterval,
        stationId: backendForm.stationId.trim(),
        timeout: backendForm.timeout,
        maxRetries: backendForm.maxRetries
      });
      setIsEditingBackend(false);
      addNotification({
        type: "success",
        title: "Success",
        message: "Backend configuration updated successfully"
      });
    } catch (error) {
      addNotification({
        type: "error",
        title: "Update Failed",
        message: error instanceof Error ? error.message : "Failed to update backend configuration"
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
                placeholder: "e.g., station_001",
                disabled: true,
                hint: "Configured in station.yaml"
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
          icon: /* @__PURE__ */ jsxRuntimeExports.jsx(FolderOpen, { className: "w-5 h-5" }),
          title: "Paths",
          isLoading: infoLoading,
          children: systemInfo && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-3", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Sequences Directory" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "span",
                {
                  className: "text-sm font-mono px-2 py-1 rounded",
                  style: {
                    backgroundColor: "var(--color-bg-tertiary)",
                    color: "var(--color-text-primary)"
                  },
                  children: systemInfo.sequencesDir || "sequences"
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Data Directory" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "span",
                {
                  className: "text-sm font-mono px-2 py-1 rounded",
                  style: {
                    backgroundColor: "var(--color-bg-tertiary)",
                    color: "var(--color-text-primary)"
                  },
                  children: systemInfo.dataDir || "data"
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
                children: "Paths are configured in station.yaml. Relative paths are resolved from project root."
              }
            )
          ] })
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
              /* @__PURE__ */ jsxRuntimeExports.jsx(StatusBadge$1, { status: "disconnected", size: "sm" })
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
          isLoading: backendLoading || healthLoading,
          action: !isEditingBackend ? /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", size: "sm", onClick: handleBackendEditStart, children: /* @__PURE__ */ jsxRuntimeExports.jsx(Pen, { className: "w-4 h-4" }) }) : null,
          children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Status" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                StatusBadge$1,
                {
                  status: (health == null ? void 0 : health.backendStatus) === "connected" ? "connected" : "disconnected",
                  size: "sm"
                }
              )
            ] }),
            isEditingBackend ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                EditableRow,
                {
                  label: "Backend URL",
                  value: backendForm.url,
                  onChange: (value) => setBackendForm((prev) => ({ ...prev, url: value })),
                  placeholder: "http://localhost:8000"
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                EditableRow,
                {
                  label: "Station ID",
                  value: backendForm.stationId,
                  onChange: (value) => setBackendForm((prev) => ({ ...prev, stationId: value })),
                  placeholder: "station_001",
                  disabled: true,
                  hint: "Must match API Key"
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between gap-4", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "label",
                  {
                    className: "text-sm whitespace-nowrap",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Sync Interval (sec)"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "input",
                  {
                    type: "number",
                    min: 5,
                    max: 3600,
                    value: backendForm.syncInterval,
                    onChange: (e) => setBackendForm((prev) => ({ ...prev, syncInterval: parseInt(e.target.value) || 30 })),
                    className: "w-24 px-3 py-1.5 text-sm rounded border outline-none transition-colors",
                    style: {
                      backgroundColor: "var(--color-bg-primary)",
                      borderColor: "var(--color-border-default)",
                      color: "var(--color-text-primary)"
                    }
                  }
                )
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between gap-4", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "label",
                  {
                    className: "text-sm whitespace-nowrap",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Timeout (sec)"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "input",
                  {
                    type: "number",
                    min: 1,
                    max: 300,
                    value: backendForm.timeout,
                    onChange: (e) => setBackendForm((prev) => ({ ...prev, timeout: parseFloat(e.target.value) || 30 })),
                    className: "w-24 px-3 py-1.5 text-sm rounded border outline-none transition-colors",
                    style: {
                      backgroundColor: "var(--color-bg-primary)",
                      borderColor: "var(--color-border-default)",
                      color: "var(--color-text-primary)"
                    }
                  }
                )
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between gap-4", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "label",
                  {
                    className: "text-sm whitespace-nowrap",
                    style: { color: "var(--color-text-secondary)" },
                    children: "Max Retries"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "input",
                  {
                    type: "number",
                    min: 0,
                    max: 10,
                    value: backendForm.maxRetries,
                    onChange: (e) => setBackendForm((prev) => ({ ...prev, maxRetries: parseInt(e.target.value) || 5 })),
                    className: "w-24 px-3 py-1.5 text-sm rounded border outline-none transition-colors",
                    style: {
                      backgroundColor: "var(--color-bg-primary)",
                      borderColor: "var(--color-border-default)",
                      color: "var(--color-text-primary)"
                    }
                  }
                )
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-end gap-2 pt-2", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  Button,
                  {
                    variant: "ghost",
                    size: "sm",
                    onClick: handleBackendEditCancel,
                    disabled: updateBackend.isPending,
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
                    onClick: handleBackendEditSave,
                    disabled: updateBackend.isPending,
                    children: [
                      updateBackend.isPending ? /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-4 h-4 mr-1 animate-spin" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Save, { className: "w-4 h-4 mr-1" }),
                      "Save"
                    ]
                  }
                )
              ] })
            ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow$1, { label: "Backend URL", value: (backendConfig == null ? void 0 : backendConfig.url) || "-" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow$1, { label: "Station ID", value: (backendConfig == null ? void 0 : backendConfig.stationId) || "-" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow$1, { label: "Sync Interval", value: backendConfig ? `${backendConfig.syncInterval}s` : "-" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow$1, { label: "Timeout", value: backendConfig ? `${backendConfig.timeout}s` : "-" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow$1, { label: "Max Retries", value: ((_a = backendConfig == null ? void 0 : backendConfig.maxRetries) == null ? void 0 : _a.toString()) || "-" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(InfoRow$1, { label: "API Key", value: (backendConfig == null ? void 0 : backendConfig.apiKeyMasked) || "-" })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "div",
              {
                className: "text-xs p-2 rounded",
                style: {
                  backgroundColor: "var(--color-bg-tertiary)",
                  color: "var(--color-text-tertiary)"
                },
                children: "API Key cannot be modified through UI for security reasons."
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
function EditableRow({ label, value, onChange, placeholder, disabled, hint }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col gap-1", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between gap-4", children: [
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
          disabled,
          className: `flex-1 px-3 py-1.5 text-sm rounded border outline-none transition-colors ${disabled ? "cursor-not-allowed opacity-60" : ""}`,
          style: {
            backgroundColor: disabled ? "var(--color-bg-tertiary)" : "var(--color-bg-primary)",
            borderColor: "var(--color-border-default)",
            color: "var(--color-text-primary)"
          }
        }
      )
    ] }),
    hint && /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs ml-auto", style: { color: "var(--color-text-tertiary)" }, children: hint })
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
                StatusBadge$1,
                {
                  status: websocketStatus === "connected" ? "connected" : "disconnected",
                  size: "sm"
                }
              )
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { style: { color: "var(--color-text-secondary)" }, children: "Backend" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                StatusBadge$1,
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
                StatusBadge$1,
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
                StatusBadge$1,
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
    /* @__PURE__ */ jsxRuntimeExports.jsx(Route, { path: ROUTES.RESULTS, element: /* @__PURE__ */ jsxRuntimeExports.jsx(ResultsPage, {}) }),
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
