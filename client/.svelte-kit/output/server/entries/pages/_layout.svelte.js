import "clsx";
function _layout($$renderer, $$props) {
  const { children } = $$props;
  children($$renderer);
  $$renderer.push(`<!---->`);
}
export {
  _layout as default
};
