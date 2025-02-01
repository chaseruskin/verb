/*!
Highlight.js v11.7.0 (git: bc1b06bb3a)
(c) 2006-2024 undefined and other contributors
License: BSD-3-Clause
*/
var hljs=function(){"use strict";var e={exports:{}};function n(e){
return e instanceof Map?e.clear=e.delete=e.set=()=>{
throw Error("map is read-only")}:e instanceof Set&&(e.add=e.clear=e.delete=()=>{
throw Error("set is read-only")
}),Object.freeze(e),Object.getOwnPropertyNames(e).forEach((t=>{var i=e[t]
;"object"!=typeof i||Object.isFrozen(i)||n(i)})),e}
e.exports=n,e.exports.default=n;class t{constructor(e){
void 0===e.data&&(e.data={}),this.data=e.data,this.isMatchIgnored=!1}
ignoreMatch(){this.isMatchIgnored=!0}}function i(e){
return e.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#x27;")
}function s(e,...n){const t=Object.create(null);for(const n in e)t[n]=e[n]
;return n.forEach((e=>{for(const n in e)t[n]=e[n]})),t}
const a=e=>!!e.scope||e.sublanguage&&e.language;class r{constructor(e,n){
this.buffer="",this.classPrefix=n.classPrefix,e.walk(this)}addText(e){
this.buffer+=i(e)}openNode(e){if(!a(e))return;let n=""
;n=e.sublanguage?"language-"+e.language:((e,{prefix:n})=>{if(e.includes(".")){
const t=e.split(".")
;return[`${n}${t.shift()}`,...t.map(((e,n)=>`${e}${"_".repeat(n+1)}`))].join(" ")
}return`${n}${e}`})(e.scope,{prefix:this.classPrefix}),this.span(n)}
closeNode(e){a(e)&&(this.buffer+="</span>")}value(){return this.buffer}span(e){
this.buffer+=`<span class="${e}">`}}const o=(e={})=>{const n={children:[]}
;return Object.assign(n,e),n};class l{constructor(){
this.rootNode=o(),this.stack=[this.rootNode]}get top(){
return this.stack[this.stack.length-1]}get root(){return this.rootNode}add(e){
this.top.children.push(e)}openNode(e){const n=o({scope:e})
;this.add(n),this.stack.push(n)}closeNode(){
if(this.stack.length>1)return this.stack.pop()}closeAllNodes(){
for(;this.closeNode(););}toJSON(){return JSON.stringify(this.rootNode,null,4)}
walk(e){return this.constructor._walk(e,this.rootNode)}static _walk(e,n){
return"string"==typeof n?e.addText(n):n.children&&(e.openNode(n),
n.children.forEach((n=>this._walk(e,n))),e.closeNode(n)),e}static _collapse(e){
"string"!=typeof e&&e.children&&(e.children.every((e=>"string"==typeof e))?e.children=[e.children.join("")]:e.children.forEach((e=>{
l._collapse(e)})))}}class c extends l{constructor(e){super(),this.options=e}
addKeyword(e,n){""!==e&&(this.openNode(n),this.addText(e),this.closeNode())}
addText(e){""!==e&&this.add(e)}addSublanguage(e,n){const t=e.root
;t.sublanguage=!0,t.language=n,this.add(t)}toHTML(){
return new r(this,this.options).value()}finalize(){return!0}}function d(e){
return e?"string"==typeof e?e:e.source:null}function g(e){return b("(?=",e,")")}
function u(e){return b("(?:",e,")*")}function h(e){return b("(?:",e,")?")}
function b(...e){return e.map((e=>d(e))).join("")}function p(...e){const n=(e=>{
const n=e[e.length-1]
;return"object"==typeof n&&n.constructor===Object?(e.splice(e.length-1,1),n):{}
})(e);return"("+(n.capture?"":"?:")+e.map((e=>d(e))).join("|")+")"}
function f(e){return RegExp(e.toString()+"|").exec("").length-1}
const m=/\[(?:[^\\\]]|\\.)*\]|\(\??|\\([1-9][0-9]*)|\\./
;function _(e,{joinWith:n}){let t=0;return e.map((e=>{t+=1;const n=t
;let i=d(e),s="";for(;i.length>0;){const e=m.exec(i);if(!e){s+=i;break}
s+=i.substring(0,e.index),
i=i.substring(e.index+e[0].length),"\\"===e[0][0]&&e[1]?s+="\\"+(Number(e[1])+n):(s+=e[0],
"("===e[0]&&t++)}return s})).map((e=>`(${e})`)).join(n)}
const $="[a-zA-Z]\\w*",y="[a-zA-Z_]\\w*",w="\\b\\d+(\\.\\d+)?",E="(-?)(\\b0[xX][a-fA-F0-9]+|(\\b\\d+(\\.\\d*)?|\\.\\d+)([eE][-+]?\\d+)?)",v="\\b(0b[01]+)",x={
begin:"\\\\[\\s\\S]",relevance:0},N={scope:"string",begin:"'",end:"'",
illegal:"\\n",contains:[x]},k={scope:"string",begin:'"',end:'"',illegal:"\\n",
contains:[x]},O=(e,n,t={})=>{const i=s({scope:"comment",begin:e,end:n,
contains:[]},t);i.contains.push({scope:"doctag",
begin:"[ ]*(?=(TODO|FIXME|NOTE|BUG|OPTIMIZE|HACK|XXX):)",
end:/(TODO|FIXME|NOTE|BUG|OPTIMIZE|HACK|XXX):/,excludeBegin:!0,relevance:0})
;const a=p("I","a","is","so","us","to","at","if","in","it","on",/[A-Za-z]+['](d|ve|re|ll|t|s|n)/,/[A-Za-z]+[-][a-z]+/,/[A-Za-z][a-z]{2,}/)
;return i.contains.push({begin:b(/[ ]+/,"(",a,/[.]?[:]?([.][ ]|[ ])/,"){3}")}),i
},A=O("//","$"),M=O("/\\*","\\*/"),S=O("#","$");var R=Object.freeze({
__proto__:null,MATCH_NOTHING_RE:/\b\B/,IDENT_RE:$,UNDERSCORE_IDENT_RE:y,
NUMBER_RE:w,C_NUMBER_RE:E,BINARY_NUMBER_RE:v,
RE_STARTERS_RE:"!|!=|!==|%|%=|&|&&|&=|\\*|\\*=|\\+|\\+=|,|-|-=|/=|/|:|;|<<|<<=|<=|<|===|==|=|>>>=|>>=|>=|>>>|>>|>|\\?|\\[|\\{|\\(|\\^|\\^=|\\||\\|=|\\|\\||~",
SHEBANG:(e={})=>{const n=/^#![ ]*\//
;return e.binary&&(e.begin=b(n,/.*\b/,e.binary,/\b.*/)),s({scope:"meta",begin:n,
end:/$/,relevance:0,"on:begin":(e,n)=>{0!==e.index&&n.ignoreMatch()}},e)},
BACKSLASH_ESCAPE:x,APOS_STRING_MODE:N,QUOTE_STRING_MODE:k,PHRASAL_WORDS_MODE:{
begin:/\b(a|an|the|are|I'm|isn't|don't|doesn't|won't|but|just|should|pretty|simply|enough|gonna|going|wtf|so|such|will|you|your|they|like|more)\b/
},COMMENT:O,C_LINE_COMMENT_MODE:A,C_BLOCK_COMMENT_MODE:M,HASH_COMMENT_MODE:S,
NUMBER_MODE:{scope:"number",begin:w,relevance:0},C_NUMBER_MODE:{scope:"number",
begin:E,relevance:0},BINARY_NUMBER_MODE:{scope:"number",begin:v,relevance:0},
REGEXP_MODE:{begin:/(?=\/[^/\n]*\/)/,contains:[{scope:"regexp",begin:/\//,
end:/\/[gimuy]*/,illegal:/\n/,contains:[x,{begin:/\[/,end:/\]/,relevance:0,
contains:[x]}]}]},TITLE_MODE:{scope:"title",begin:$,relevance:0},
UNDERSCORE_TITLE_MODE:{scope:"title",begin:y,relevance:0},METHOD_GUARD:{
begin:"\\.\\s*[a-zA-Z_]\\w*",relevance:0},END_SAME_AS_BEGIN:e=>Object.assign(e,{
"on:begin":(e,n)=>{n.data._beginMatch=e[1]},"on:end":(e,n)=>{
n.data._beginMatch!==e[1]&&n.ignoreMatch()}})});function B(e,n){
"."===e.input[e.index-1]&&n.ignoreMatch()}function T(e,n){
void 0!==e.className&&(e.scope=e.className,delete e.className)}function I(e,n){
n&&e.beginKeywords&&(e.begin="\\b("+e.beginKeywords.split(" ").join("|")+")(?!\\.)(?=\\b|\\s)",
e.__beforeBegin=B,e.keywords=e.keywords||e.beginKeywords,delete e.beginKeywords,
void 0===e.relevance&&(e.relevance=0))}function j(e,n){
Array.isArray(e.illegal)&&(e.illegal=p(...e.illegal))}function C(e,n){
if(e.match){
if(e.begin||e.end)throw Error("begin & end are not supported with match")
;e.begin=e.match,delete e.match}}function L(e,n){
void 0===e.relevance&&(e.relevance=1)}const D=(e,n)=>{if(!e.beforeMatch)return
;if(e.starts)throw Error("beforeMatch cannot be used with starts")
;const t=Object.assign({},e);Object.keys(e).forEach((n=>{delete e[n]
})),e.keywords=t.keywords,e.begin=b(t.beforeMatch,g(t.begin)),e.starts={
relevance:0,contains:[Object.assign(t,{endsParent:!0})]
},e.relevance=0,delete t.beforeMatch
},H=["of","and","for","in","not","or","if","then","parent","list","value"]
;function P(e,n,t="keyword"){const i=Object.create(null)
;return"string"==typeof e?s(t,e.split(" ")):Array.isArray(e)?s(t,e):Object.keys(e).forEach((t=>{
Object.assign(i,P(e[t],n,t))})),i;function s(e,t){
n&&(t=t.map((e=>e.toLowerCase()))),t.forEach((n=>{const t=n.split("|")
;i[t[0]]=[e,z(t[0],t[1])]}))}}function z(e,n){
return n?Number(n):(e=>H.includes(e.toLowerCase()))(e)?0:1}const U={},q=e=>{
console.error(e)},K=(e,...n)=>{console.log("WARN: "+e,...n)},W=(e,n)=>{
U[`${e}/${n}`]||(console.log(`Deprecated as of ${e}. ${n}`),U[`${e}/${n}`]=!0)
},Z=Error();function F(e,n,{key:t}){let i=0;const s=e[t],a={},r={}
;for(let e=1;e<=n.length;e++)r[e+i]=s[e],a[e+i]=!0,i+=f(n[e-1])
;e[t]=r,e[t]._emit=a,e[t]._multi=!0}function G(e){(e=>{
e.scope&&"object"==typeof e.scope&&null!==e.scope&&(e.beginScope=e.scope,
delete e.scope)})(e),"string"==typeof e.beginScope&&(e.beginScope={
_wrap:e.beginScope}),"string"==typeof e.endScope&&(e.endScope={_wrap:e.endScope
}),(e=>{if(Array.isArray(e.begin)){
if(e.skip||e.excludeBegin||e.returnBegin)throw q("skip, excludeBegin, returnBegin not compatible with beginScope: {}"),
Z
;if("object"!=typeof e.beginScope||null===e.beginScope)throw q("beginScope must be object"),
Z;F(e,e.begin,{key:"beginScope"}),e.begin=_(e.begin,{joinWith:""})}})(e),(e=>{
if(Array.isArray(e.end)){
if(e.skip||e.excludeEnd||e.returnEnd)throw q("skip, excludeEnd, returnEnd not compatible with endScope: {}"),
Z
;if("object"!=typeof e.endScope||null===e.endScope)throw q("endScope must be object"),
Z;F(e,e.end,{key:"endScope"}),e.end=_(e.end,{joinWith:""})}})(e)}function X(e){
function n(n,t){
return RegExp(d(n),"m"+(e.case_insensitive?"i":"")+(e.unicodeRegex?"u":"")+(t?"g":""))
}class t{constructor(){
this.matchIndexes={},this.regexes=[],this.matchAt=1,this.position=0}
addRule(e,n){
n.position=this.position++,this.matchIndexes[this.matchAt]=n,this.regexes.push([n,e]),
this.matchAt+=f(e)+1}compile(){0===this.regexes.length&&(this.exec=()=>null)
;const e=this.regexes.map((e=>e[1]));this.matcherRe=n(_(e,{joinWith:"|"
}),!0),this.lastIndex=0}exec(e){this.matcherRe.lastIndex=this.lastIndex
;const n=this.matcherRe.exec(e);if(!n)return null
;const t=n.findIndex(((e,n)=>n>0&&void 0!==e)),i=this.matchIndexes[t]
;return n.splice(0,t),Object.assign(n,i)}}class i{constructor(){
this.rules=[],this.multiRegexes=[],
this.count=0,this.lastIndex=0,this.regexIndex=0}getMatcher(e){
if(this.multiRegexes[e])return this.multiRegexes[e];const n=new t
;return this.rules.slice(e).forEach((([e,t])=>n.addRule(e,t))),
n.compile(),this.multiRegexes[e]=n,n}resumingScanAtSamePosition(){
return 0!==this.regexIndex}considerAll(){this.regexIndex=0}addRule(e,n){
this.rules.push([e,n]),"begin"===n.type&&this.count++}exec(e){
const n=this.getMatcher(this.regexIndex);n.lastIndex=this.lastIndex
;let t=n.exec(e)
;if(this.resumingScanAtSamePosition())if(t&&t.index===this.lastIndex);else{
const n=this.getMatcher(0);n.lastIndex=this.lastIndex+1,t=n.exec(e)}
return t&&(this.regexIndex+=t.position+1,
this.regexIndex===this.count&&this.considerAll()),t}}
if(e.compilerExtensions||(e.compilerExtensions=[]),
e.contains&&e.contains.includes("self"))throw Error("ERR: contains `self` is not supported at the top-level of a language.  See documentation.")
;return e.classNameAliases=s(e.classNameAliases||{}),function t(a,r){const o=a
;if(a.isCompiled)return o
;[T,C,G,D].forEach((e=>e(a,r))),e.compilerExtensions.forEach((e=>e(a,r))),
a.__beforeBegin=null,[I,j,L].forEach((e=>e(a,r))),a.isCompiled=!0;let l=null
;return"object"==typeof a.keywords&&a.keywords.$pattern&&(a.keywords=Object.assign({},a.keywords),
l=a.keywords.$pattern,
delete a.keywords.$pattern),l=l||/\w+/,a.keywords&&(a.keywords=P(a.keywords,e.case_insensitive)),
o.keywordPatternRe=n(l,!0),
r&&(a.begin||(a.begin=/\B|\b/),o.beginRe=n(o.begin),a.end||a.endsWithParent||(a.end=/\B|\b/),
a.end&&(o.endRe=n(o.end)),
o.terminatorEnd=d(o.end)||"",a.endsWithParent&&r.terminatorEnd&&(o.terminatorEnd+=(a.end?"|":"")+r.terminatorEnd)),
a.illegal&&(o.illegalRe=n(a.illegal)),
a.contains||(a.contains=[]),a.contains=[].concat(...a.contains.map((e=>(e=>(e.variants&&!e.cachedVariants&&(e.cachedVariants=e.variants.map((n=>s(e,{
variants:null},n)))),e.cachedVariants?e.cachedVariants:Q(e)?s(e,{
starts:e.starts?s(e.starts):null
}):Object.isFrozen(e)?s(e):e))("self"===e?a:e)))),a.contains.forEach((e=>{t(e,o)
})),a.starts&&t(a.starts,r),o.matcher=(e=>{const n=new i
;return e.contains.forEach((e=>n.addRule(e.begin,{rule:e,type:"begin"
}))),e.terminatorEnd&&n.addRule(e.terminatorEnd,{type:"end"
}),e.illegal&&n.addRule(e.illegal,{type:"illegal"}),n})(o),o}(e)}function Q(e){
return!!e&&(e.endsWithParent||Q(e.starts))}class V extends Error{
constructor(e,n){super(e),this.name="HTMLInjectionError",this.html=n}}
const Y=i,J=s,ee=Symbol("nomatch");var ne=(n=>{
const i=Object.create(null),s=Object.create(null),a=[];let r=!0
;const o="Could not find the language '{}', did you forget to load/include a language module?",l={
disableAutodetect:!0,name:"Plain text",contains:[]};let d={
ignoreUnescapedHTML:!1,throwUnescapedHTML:!1,noHighlightRe:/^(no-?highlight)$/i,
languageDetectRe:/\blang(?:uage)?-([\w-]+)\b/i,classPrefix:"hljs-",
cssSelector:"pre code",languages:null,__emitter:c};function f(e){
return d.noHighlightRe.test(e)}function m(e,n,t){let i="",s=""
;"object"==typeof n?(i=e,
t=n.ignoreIllegals,s=n.language):(W("10.7.0","highlight(lang, code, ...args) has been deprecated."),
W("10.7.0","Please use highlight(code, options) instead.\nhttps://github.com/highlightjs/highlight.js/issues/2277"),
s=e,i=n),void 0===t&&(t=!0);const a={code:i,language:s};k("before:highlight",a)
;const r=a.result?a.result:_(a.language,a.code,t)
;return r.code=a.code,k("after:highlight",r),r}function _(e,n,s,a){
const l=Object.create(null);function c(){if(!N.keywords)return void O.addText(A)
;let e=0;N.keywordPatternRe.lastIndex=0;let n=N.keywordPatternRe.exec(A),t=""
;for(;n;){t+=A.substring(e,n.index)
;const s=w.case_insensitive?n[0].toLowerCase():n[0],a=(i=s,N.keywords[i]);if(a){
const[e,i]=a
;if(O.addText(t),t="",l[s]=(l[s]||0)+1,l[s]<=7&&(M+=i),e.startsWith("_"))t+=n[0];else{
const t=w.classNameAliases[e]||e;O.addKeyword(n[0],t)}}else t+=n[0]
;e=N.keywordPatternRe.lastIndex,n=N.keywordPatternRe.exec(A)}var i
;t+=A.substring(e),O.addText(t)}function g(){null!=N.subLanguage?(()=>{
if(""===A)return;let e=null;if("string"==typeof N.subLanguage){
if(!i[N.subLanguage])return void O.addText(A)
;e=_(N.subLanguage,A,!0,k[N.subLanguage]),k[N.subLanguage]=e._top
}else e=$(A,N.subLanguage.length?N.subLanguage:null)
;N.relevance>0&&(M+=e.relevance),O.addSublanguage(e._emitter,e.language)
})():c(),A=""}function u(e,n){let t=1;const i=n.length-1;for(;t<=i;){
if(!e._emit[t]){t++;continue}const i=w.classNameAliases[e[t]]||e[t],s=n[t]
;i?O.addKeyword(s,i):(A=s,c(),A=""),t++}}function h(e,n){
return e.scope&&"string"==typeof e.scope&&O.openNode(w.classNameAliases[e.scope]||e.scope),
e.beginScope&&(e.beginScope._wrap?(O.addKeyword(A,w.classNameAliases[e.beginScope._wrap]||e.beginScope._wrap),
A=""):e.beginScope._multi&&(u(e.beginScope,n),A="")),N=Object.create(e,{parent:{
value:N}}),N}function b(e,n,i){let s=((e,n)=>{const t=e&&e.exec(n)
;return t&&0===t.index})(e.endRe,i);if(s){if(e["on:end"]){const i=new t(e)
;e["on:end"](n,i),i.isMatchIgnored&&(s=!1)}if(s){
for(;e.endsParent&&e.parent;)e=e.parent;return e}}
if(e.endsWithParent)return b(e.parent,n,i)}function p(e){
return 0===N.matcher.regexIndex?(A+=e[0],1):(B=!0,0)}function f(e){
const t=e[0],i=n.substring(e.index),s=b(N,e,i);if(!s)return ee;const a=N
;N.endScope&&N.endScope._wrap?(g(),
O.addKeyword(t,N.endScope._wrap)):N.endScope&&N.endScope._multi?(g(),
u(N.endScope,e)):a.skip?A+=t:(a.returnEnd||a.excludeEnd||(A+=t),
g(),a.excludeEnd&&(A=t));do{
N.scope&&O.closeNode(),N.skip||N.subLanguage||(M+=N.relevance),N=N.parent
}while(N!==s.parent);return s.starts&&h(s.starts,e),a.returnEnd?0:t.length}
let m={};function y(i,a){const o=a&&a[0];if(A+=i,null==o)return g(),0
;if("begin"===m.type&&"end"===a.type&&m.index===a.index&&""===o){
if(A+=n.slice(a.index,a.index+1),!r){const n=Error(`0 width match regex (${e})`)
;throw n.languageName=e,n.badRule=m.rule,n}return 1}
if(m=a,"begin"===a.type)return(e=>{
const n=e[0],i=e.rule,s=new t(i),a=[i.__beforeBegin,i["on:begin"]]
;for(const t of a)if(t&&(t(e,s),s.isMatchIgnored))return p(n)
;return i.skip?A+=n:(i.excludeBegin&&(A+=n),
g(),i.returnBegin||i.excludeBegin||(A=n)),h(i,e),i.returnBegin?0:n.length})(a)
;if("illegal"===a.type&&!s){
const e=Error('Illegal lexeme "'+o+'" for mode "'+(N.scope||"<unnamed>")+'"')
;throw e.mode=N,e}if("end"===a.type){const e=f(a);if(e!==ee)return e}
if("illegal"===a.type&&""===o)return 1
;if(R>1e5&&R>3*a.index)throw Error("potential infinite loop, way more iterations than matches")
;return A+=o,o.length}const w=v(e)
;if(!w)throw q(o.replace("{}",e)),Error('Unknown language: "'+e+'"')
;const E=X(w);let x="",N=a||E;const k={},O=new d.__emitter(d);(()=>{const e=[]
;for(let n=N;n!==w;n=n.parent)n.scope&&e.unshift(n.scope)
;e.forEach((e=>O.openNode(e)))})();let A="",M=0,S=0,R=0,B=!1;try{
for(N.matcher.considerAll();;){
R++,B?B=!1:N.matcher.considerAll(),N.matcher.lastIndex=S
;const e=N.matcher.exec(n);if(!e)break;const t=y(n.substring(S,e.index),e)
;S=e.index+t}
return y(n.substring(S)),O.closeAllNodes(),O.finalize(),x=O.toHTML(),{
language:e,value:x,relevance:M,illegal:!1,_emitter:O,_top:N}}catch(t){
if(t.message&&t.message.includes("Illegal"))return{language:e,value:Y(n),
illegal:!0,relevance:0,_illegalBy:{message:t.message,index:S,
context:n.slice(S-100,S+100),mode:t.mode,resultSoFar:x},_emitter:O};if(r)return{
language:e,value:Y(n),illegal:!1,relevance:0,errorRaised:t,_emitter:O,_top:N}
;throw t}}function $(e,n){n=n||d.languages||Object.keys(i);const t=(e=>{
const n={value:Y(e),illegal:!1,relevance:0,_top:l,_emitter:new d.__emitter(d)}
;return n._emitter.addText(e),n})(e),s=n.filter(v).filter(N).map((n=>_(n,e,!1)))
;s.unshift(t);const a=s.sort(((e,n)=>{
if(e.relevance!==n.relevance)return n.relevance-e.relevance
;if(e.language&&n.language){if(v(e.language).supersetOf===n.language)return 1
;if(v(n.language).supersetOf===e.language)return-1}return 0})),[r,o]=a,c=r
;return c.secondBest=o,c}function y(e){let n=null;const t=(e=>{
let n=e.className+" ";n+=e.parentNode?e.parentNode.className:""
;const t=d.languageDetectRe.exec(n);if(t){const n=v(t[1])
;return n||(K(o.replace("{}",t[1])),
K("Falling back to no-highlight mode for this block.",e)),n?t[1]:"no-highlight"}
return n.split(/\s+/).find((e=>f(e)||v(e)))})(e);if(f(t))return
;if(k("before:highlightElement",{el:e,language:t
}),e.children.length>0&&(d.ignoreUnescapedHTML||(console.warn("One of your code blocks includes unescaped HTML. This is a potentially serious security risk."),
console.warn("https://github.com/highlightjs/highlight.js/wiki/security"),
console.warn("The element with unescaped HTML:"),
console.warn(e)),d.throwUnescapedHTML))throw new V("One of your code blocks includes unescaped HTML.",e.innerHTML)
;n=e;const i=n.textContent,a=t?m(i,{language:t,ignoreIllegals:!0}):$(i)
;e.innerHTML=a.value,((e,n,t)=>{const i=n&&s[n]||t
;e.classList.add("hljs"),e.classList.add("language-"+i)
})(e,t,a.language),e.result={language:a.language,re:a.relevance,
relevance:a.relevance},a.secondBest&&(e.secondBest={
language:a.secondBest.language,relevance:a.secondBest.relevance
}),k("after:highlightElement",{el:e,result:a,text:i})}let w=!1;function E(){
"loading"!==document.readyState?document.querySelectorAll(d.cssSelector).forEach(y):w=!0
}function v(e){return e=(e||"").toLowerCase(),i[e]||i[s[e]]}
function x(e,{languageName:n}){"string"==typeof e&&(e=[e]),e.forEach((e=>{
s[e.toLowerCase()]=n}))}function N(e){const n=v(e)
;return n&&!n.disableAutodetect}function k(e,n){const t=e;a.forEach((e=>{
e[t]&&e[t](n)}))}
"undefined"!=typeof window&&window.addEventListener&&window.addEventListener("DOMContentLoaded",(()=>{
w&&E()}),!1),Object.assign(n,{highlight:m,highlightAuto:$,highlightAll:E,
highlightElement:y,
highlightBlock:e=>(W("10.7.0","highlightBlock will be removed entirely in v12.0"),
W("10.7.0","Please use highlightElement now."),y(e)),configure:e=>{d=J(d,e)},
initHighlighting:()=>{
E(),W("10.6.0","initHighlighting() deprecated.  Use highlightAll() now.")},
initHighlightingOnLoad:()=>{
E(),W("10.6.0","initHighlightingOnLoad() deprecated.  Use highlightAll() now.")
},registerLanguage:(e,t)=>{let s=null;try{s=t(n)}catch(n){
if(q("Language definition for '{}' could not be registered.".replace("{}",e)),
!r)throw n;q(n),s=l}
s.name||(s.name=e),i[e]=s,s.rawDefinition=t.bind(null,n),s.aliases&&x(s.aliases,{
languageName:e})},unregisterLanguage:e=>{delete i[e]
;for(const n of Object.keys(s))s[n]===e&&delete s[n]},
listLanguages:()=>Object.keys(i),getLanguage:v,registerAliases:x,
autoDetection:N,inherit:J,addPlugin:e=>{(e=>{
e["before:highlightBlock"]&&!e["before:highlightElement"]&&(e["before:highlightElement"]=n=>{
e["before:highlightBlock"](Object.assign({block:n.el},n))
}),e["after:highlightBlock"]&&!e["after:highlightElement"]&&(e["after:highlightElement"]=n=>{
e["after:highlightBlock"](Object.assign({block:n.el},n))})})(e),a.push(e)}
}),n.debugMode=()=>{r=!1},n.safeMode=()=>{r=!0
},n.versionString="11.7.0",n.regex={concat:b,lookahead:g,either:p,optional:h,
anyNumberOfTimes:u};for(const n in R)"object"==typeof R[n]&&e.exports(R[n])
;return Object.assign(n,R),n})({}),te=Object.freeze({__proto__:null,
grmr_veryl:e=>({name:"Veryl",aliases:["veryl"],case_insensitive:!1,keywords:{
keyword:"module interface function modport package enum struct param local clock clock_posedge clock_negedge reset reset_async_high reset_async_low reset_sync_high reset_sync_low always_ff always_comb assign return as var inst import export logic bit tri signed u32 u64 i32 i64 f32 f64 input output inout ref if if_reset else for in case switch step repeat initial final inside outside default pub let break embed include unsafe type const proto",
literal:""},
contains:[e.QUOTE_STRING_MODE,e.C_BLOCK_COMMENT_MODE,e.C_LINE_COMMENT_MODE,{
scope:"number",contains:[e.BACKSLASH_ESCAPE],variants:[{
begin:/\b((\d+'([bhodBHOD]))[0-9xzXZa-fA-F_]+)/},{
begin:/\B(('([bhodBHOD]))[0-9xzXZa-fA-F_]+)/},{begin:/\b[0-9][0-9_]*/,
relevance:0}]}]}),grmr_verilog:e=>{
const n=e.regex,t=["begin_keywords","celldefine","default_nettype","default_decay_time","default_trireg_strength","define","delay_mode_distributed","delay_mode_path","delay_mode_unit","delay_mode_zero","else","elsif","end_keywords","endcelldefine","endif","ifdef","ifndef","include","line","nounconnected_drive","pragma","resetall","timescale","unconnected_drive","undef","undefineall"]
;return{name:"Verilog",aliases:["v","sv","svh"],case_insensitive:!1,keywords:{
$pattern:/\$?[\w]+(\$[\w]+)*/,
keyword:["accept_on","alias","always","always_comb","always_ff","always_latch","and","assert","assign","assume","automatic","before","begin","bind","bins","binsof","bit","break","buf|0","bufif0","bufif1","byte","case","casex","casez","cell","chandle","checker","class","clocking","cmos","config","const","constraint","context","continue","cover","covergroup","coverpoint","cross","deassign","default","defparam","design","disable","dist","do","edge","else","end","endcase","endchecker","endclass","endclocking","endconfig","endfunction","endgenerate","endgroup","endinterface","endmodule","endpackage","endprimitive","endprogram","endproperty","endspecify","endsequence","endtable","endtask","enum","event","eventually","expect","export","extends","extern","final","first_match","for","force","foreach","forever","fork","forkjoin","function","generate|5","genvar","global","highz0","highz1","if","iff","ifnone","ignore_bins","illegal_bins","implements","implies","import","incdir","include","initial","inout","input","inside","instance","int","integer","interconnect","interface","intersect","join","join_any","join_none","large","let","liblist","library","local","localparam","logic","longint","macromodule","matches","medium","modport","module","nand","negedge","nettype","new","nexttime","nmos","nor","noshowcancelled","not","notif0","notif1","or","output","package","packed","parameter","pmos","posedge","primitive","priority","program","property","protected","pull0","pull1","pulldown","pullup","pulsestyle_ondetect","pulsestyle_onevent","pure","rand","randc","randcase","randsequence","rcmos","real","realtime","ref","reg","reject_on","release","repeat","restrict","return","rnmos","rpmos","rtran","rtranif0","rtranif1","s_always","s_eventually","s_nexttime","s_until","s_until_with","scalared","sequence","shortint","shortreal","showcancelled","signed","small","soft","solve","specify","specparam","static","string","strong","strong0","strong1","struct","super","supply0","supply1","sync_accept_on","sync_reject_on","table","tagged","task","this","throughout","time","timeprecision","timeunit","tran","tranif0","tranif1","tri","tri0","tri1","triand","trior","trireg","type","typedef","union","unique","unique0","unsigned","until","until_with","untyped","use","uwire","var","vectored","virtual","void","wait","wait_order","wand","weak","weak0","weak1","while","wildcard","wire","with","within","wor","xnor","xor"],
literal:["null"],
built_in:["$finish","$stop","$exit","$fatal","$error","$warning","$info","$realtime","$time","$printtimescale","$bitstoreal","$bitstoshortreal","$itor","$signed","$cast","$bits","$stime","$timeformat","$realtobits","$shortrealtobits","$rtoi","$unsigned","$asserton","$assertkill","$assertpasson","$assertfailon","$assertnonvacuouson","$assertoff","$assertcontrol","$assertpassoff","$assertfailoff","$assertvacuousoff","$isunbounded","$sampled","$fell","$changed","$past_gclk","$fell_gclk","$changed_gclk","$rising_gclk","$steady_gclk","$coverage_control","$coverage_get","$coverage_save","$set_coverage_db_name","$rose","$stable","$past","$rose_gclk","$stable_gclk","$future_gclk","$falling_gclk","$changing_gclk","$display","$coverage_get_max","$coverage_merge","$get_coverage","$load_coverage_db","$typename","$unpacked_dimensions","$left","$low","$increment","$clog2","$ln","$log10","$exp","$sqrt","$pow","$floor","$ceil","$sin","$cos","$tan","$countbits","$onehot","$isunknown","$fatal","$warning","$dimensions","$right","$high","$size","$asin","$acos","$atan","$atan2","$hypot","$sinh","$cosh","$tanh","$asinh","$acosh","$atanh","$countones","$onehot0","$error","$info","$random","$dist_chi_square","$dist_erlang","$dist_exponential","$dist_normal","$dist_poisson","$dist_t","$dist_uniform","$q_initialize","$q_remove","$q_exam","$async$and$array","$async$nand$array","$async$or$array","$async$nor$array","$sync$and$array","$sync$nand$array","$sync$or$array","$sync$nor$array","$q_add","$q_full","$psprintf","$async$and$plane","$async$nand$plane","$async$or$plane","$async$nor$plane","$sync$and$plane","$sync$nand$plane","$sync$or$plane","$sync$nor$plane","$system","$display","$displayb","$displayh","$displayo","$strobe","$strobeb","$strobeh","$strobeo","$write","$readmemb","$readmemh","$writememh","$value$plusargs","$dumpvars","$dumpon","$dumplimit","$dumpports","$dumpportson","$dumpportslimit","$writeb","$writeh","$writeo","$monitor","$monitorb","$monitorh","$monitoro","$writememb","$dumpfile","$dumpoff","$dumpall","$dumpflush","$dumpportsoff","$dumpportsall","$dumpportsflush","$fclose","$fdisplay","$fdisplayb","$fdisplayh","$fdisplayo","$fstrobe","$fstrobeb","$fstrobeh","$fstrobeo","$swrite","$swriteb","$swriteh","$swriteo","$fscanf","$fread","$fseek","$fflush","$feof","$fopen","$fwrite","$fwriteb","$fwriteh","$fwriteo","$fmonitor","$fmonitorb","$fmonitorh","$fmonitoro","$sformat","$sformatf","$fgetc","$ungetc","$fgets","$sscanf","$rewind","$ftell","$ferror"]
},contains:[e.C_BLOCK_COMMENT_MODE,e.C_LINE_COMMENT_MODE,e.QUOTE_STRING_MODE,{
scope:"number",contains:[e.BACKSLASH_ESCAPE],variants:[{
begin:/\b((\d+'([bhodBHOD]))[0-9xzXZa-fA-F_]+)/},{
begin:/\B(('([bhodBHOD]))[0-9xzXZa-fA-F_]+)/},{begin:/\b[0-9][0-9_]*/,
relevance:0}]},{scope:"variable",variants:[{begin:"#\\((?!parameter).+\\)"},{
begin:"\\.\\w+",relevance:0}]},{scope:"variable.constant",
match:n.concat(/`/,n.either("__FILE__","__LINE__"))},{scope:"meta",
begin:n.concat(/`/,n.either(...t)),end:/$|\/\/|\/\*/,returnEnd:!0,keywords:t}]}
},grmr_ini:e=>{const n=e.regex,t={className:"number",relevance:0,variants:[{
begin:/([+-]+)?[\d]+_[\d_]+/},{begin:e.NUMBER_RE}]},i=e.COMMENT();i.variants=[{
begin:/;/,end:/$/},{begin:/#/,end:/$/}];const s={className:"variable",
variants:[{begin:/\$[\w\d"][\w\d_]*/},{begin:/\$\{(.*?)\}/}]},a={
className:"literal",begin:/\bon|off|true|false|yes|no\b/},r={className:"string",
contains:[e.BACKSLASH_ESCAPE],variants:[{begin:"'''",end:"'''",relevance:10},{
begin:'"""',end:'"""',relevance:10},{begin:'"',end:'"'},{begin:"'",end:"'"}]
},o={begin:/\[/,end:/\]/,contains:[i,a,s,r,t,"self"],relevance:0
},l=n.either(/[A-Za-z0-9_-]+/,/"(\\"|[^"])*"/,/'[^']*'/);return{
name:"TOML, also INI",aliases:["toml"],case_insensitive:!0,illegal:/\S/,
contains:[i,{className:"section",begin:/\[+/,end:/\]+/},{
begin:n.concat(l,"(\\s*\\.\\s*",l,")*",n.lookahead(/\s*=\s*[^#\s]/)),
className:"attr",starts:{end:/$/,contains:[i,o,a,s,r,t]}}]}},grmr_ruby:e=>{
const n=e.regex,t="([a-zA-Z_]\\w*[!?=]?|[-+~]@|<<|>>|=~|===?|<=>|[<>]=?|\\*\\*|[-/+%^&*~`|]|\\[\\]=?)",i=n.either(/\b([A-Z]+[a-z0-9]+)+/,/\b([A-Z]+[a-z0-9]+)+[A-Z]+/),s=n.concat(i,/(::\w+)*/),a={
"variable.constant":["__FILE__","__LINE__","__ENCODING__"],
"variable.language":["self","super"],
keyword:["alias","and","begin","BEGIN","break","case","class","defined","do","else","elsif","end","END","ensure","for","if","in","module","next","not","or","redo","require","rescue","retry","return","then","undef","unless","until","when","while","yield","include","extend","prepend","public","private","protected","raise","throw"],
built_in:["proc","lambda","attr_accessor","attr_reader","attr_writer","define_method","private_constant","module_function"],
literal:["true","false","nil"]},r={className:"doctag",begin:"@[A-Za-z]+"},o={
begin:"#<",end:">"},l=[e.COMMENT("#","$",{contains:[r]
}),e.COMMENT("^=begin","^=end",{contains:[r],relevance:10
}),e.COMMENT("^__END__",e.MATCH_NOTHING_RE)],c={className:"subst",begin:/#\{/,
end:/\}/,keywords:a},d={className:"string",contains:[e.BACKSLASH_ESCAPE,c],
variants:[{begin:/'/,end:/'/},{begin:/"/,end:/"/},{begin:/`/,end:/`/},{
begin:/%[qQwWx]?\(/,end:/\)/},{begin:/%[qQwWx]?\[/,end:/\]/},{
begin:/%[qQwWx]?\{/,end:/\}/},{begin:/%[qQwWx]?</,end:/>/},{begin:/%[qQwWx]?\//,
end:/\//},{begin:/%[qQwWx]?%/,end:/%/},{begin:/%[qQwWx]?-/,end:/-/},{
begin:/%[qQwWx]?\|/,end:/\|/},{begin:/\B\?(\\\d{1,3})/},{
begin:/\B\?(\\x[A-Fa-f0-9]{1,2})/},{begin:/\B\?(\\u\{?[A-Fa-f0-9]{1,6}\}?)/},{
begin:/\B\?(\\M-\\C-|\\M-\\c|\\c\\M-|\\M-|\\C-\\M-)[\x20-\x7e]/},{
begin:/\B\?\\(c|C-)[\x20-\x7e]/},{begin:/\B\?\\?\S/},{
begin:n.concat(/<<[-~]?'?/,n.lookahead(/(\w+)(?=\W)[^\n]*\n(?:[^\n]*\n)*?\s*\1\b/)),
contains:[e.END_SAME_AS_BEGIN({begin:/(\w+)/,end:/(\w+)/,
contains:[e.BACKSLASH_ESCAPE,c]})]}]},g="[0-9](_?[0-9])*",u={className:"number",
relevance:0,variants:[{
begin:`\\b([1-9](_?[0-9])*|0)(\\.(${g}))?([eE][+-]?(${g})|r)?i?\\b`},{
begin:"\\b0[dD][0-9](_?[0-9])*r?i?\\b"},{begin:"\\b0[bB][0-1](_?[0-1])*r?i?\\b"
},{begin:"\\b0[oO][0-7](_?[0-7])*r?i?\\b"},{
begin:"\\b0[xX][0-9a-fA-F](_?[0-9a-fA-F])*r?i?\\b"},{
begin:"\\b0(_?[0-7])+r?i?\\b"}]},h={variants:[{match:/\(\)/},{
className:"params",begin:/\(/,end:/(?=\))/,excludeBegin:!0,endsParent:!0,
keywords:a}]},b=[d,{variants:[{match:[/class\s+/,s,/\s+<\s+/,s]},{
match:[/\b(class|module)\s+/,s]}],scope:{2:"title.class",
4:"title.class.inherited"},keywords:a},{match:[/(include|extend)\s+/,s],scope:{
2:"title.class"},keywords:a},{relevance:0,match:[s,/\.new[. (]/],scope:{
1:"title.class"}},{relevance:0,match:/\b[A-Z][A-Z_0-9]+\b/,
className:"variable.constant"},{relevance:0,match:i,scope:"title.class"},{
match:[/def/,/\s+/,t],scope:{1:"keyword",3:"title.function"},contains:[h]},{
begin:e.IDENT_RE+"::"},{className:"symbol",
begin:e.UNDERSCORE_IDENT_RE+"(!|\\?)?:",relevance:0},{className:"symbol",
begin:":(?!\\s)",contains:[d,{begin:t}],relevance:0},u,{className:"variable",
begin:"(\\$\\W)|((\\$|@@?)(\\w+))(?=[^@$?])(?![A-Za-z])(?![@$?'])"},{
className:"params",begin:/\|/,end:/\|/,excludeBegin:!0,excludeEnd:!0,
relevance:0,keywords:a},{begin:"("+e.RE_STARTERS_RE+"|unless)\\s*",
keywords:"unless",contains:[{className:"regexp",contains:[e.BACKSLASH_ESCAPE,c],
illegal:/\n/,variants:[{begin:"/",end:"/[a-z]*"},{begin:/%r\{/,end:/\}[a-z]*/},{
begin:"%r\\(",end:"\\)[a-z]*"},{begin:"%r!",end:"![a-z]*"},{begin:"%r\\[",
end:"\\][a-z]*"}]}].concat(o,l),relevance:0}].concat(o,l)
;c.contains=b,h.contains=b;const p=[{begin:/^\s*=>/,starts:{end:"$",contains:b}
},{className:"meta.prompt",
begin:"^([>?]>|[\\w#]+\\(\\w+\\):\\d+:\\d+[>*]|(\\w+-)?\\d+\\.\\d+\\.\\d+(p\\d+)?[^\\d][^>]+>)(?=[ ])",
starts:{end:"$",keywords:a,contains:b}}];return l.unshift(o),{name:"Ruby",
aliases:["rb","gemspec","podspec","thor","irb"],keywords:a,illegal:/\/\*/,
contains:[e.SHEBANG({binary:"ruby"})].concat(p).concat(l).concat(b)}},
grmr_yaml:e=>{
const n="true false yes no null",t="[\\w#;/?:@&=+$,.~*'()[\\]]+",i={
className:"string",relevance:0,variants:[{begin:/'/,end:/'/},{begin:/"/,end:/"/
},{begin:/\S+/}],contains:[e.BACKSLASH_ESCAPE,{className:"template-variable",
variants:[{begin:/\{\{/,end:/\}\}/},{begin:/%\{/,end:/\}/}]}]},s=e.inherit(i,{
variants:[{begin:/'/,end:/'/},{begin:/"/,end:/"/},{begin:/[^\s,{}[\]]+/}]}),a={
end:",",endsWithParent:!0,excludeEnd:!0,keywords:n,relevance:0},r={begin:/\{/,
end:/\}/,contains:[a],illegal:"\\n",relevance:0},o={begin:"\\[",end:"\\]",
contains:[a],illegal:"\\n",relevance:0},l=[{className:"attr",variants:[{
begin:"\\w[\\w :\\/.-]*:(?=[ \t]|$)"},{begin:'"\\w[\\w :\\/.-]*":(?=[ \t]|$)'},{
begin:"'\\w[\\w :\\/.-]*':(?=[ \t]|$)"}]},{className:"meta",begin:"^---\\s*$",
relevance:10},{className:"string",
begin:"[\\|>]([1-9]?[+-])?[ ]*\\n( +)[^ ][^\\n]*\\n(\\2[^\\n]+\\n?)*"},{
begin:"<%[%=-]?",end:"[%-]?%>",subLanguage:"ruby",excludeBegin:!0,excludeEnd:!0,
relevance:0},{className:"type",begin:"!\\w+!"+t},{className:"type",
begin:"!<"+t+">"},{className:"type",begin:"!"+t},{className:"type",begin:"!!"+t
},{className:"meta",begin:"&"+e.UNDERSCORE_IDENT_RE+"$"},{className:"meta",
begin:"\\*"+e.UNDERSCORE_IDENT_RE+"$"},{className:"bullet",begin:"-(?=[ ]|$)",
relevance:0},e.HASH_COMMENT_MODE,{beginKeywords:n,keywords:{literal:n}},{
className:"number",
begin:"\\b[0-9]{4}(-[0-9][0-9]){0,2}([Tt \\t][0-9][0-9]?(:[0-9][0-9]){2})?(\\.[0-9]*)?([ \\t])*(Z|[-+][0-9][0-9]?(:[0-9][0-9])?)?\\b"
},{className:"number",begin:e.C_NUMBER_RE+"\\b",relevance:0},r,o,i],c=[...l]
;return c.pop(),c.push(s),a.contains=c,{name:"YAML",case_insensitive:!0,
aliases:["yml"],contains:l}}});const ie=ne;for(const e of Object.keys(te)){
const n=e.replace("grmr_","").replace("_","-");ie.registerLanguage(n,te[e])}
return ie}()
;"object"==typeof exports&&"undefined"!=typeof module&&(module.exports=hljs);