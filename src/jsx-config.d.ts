// Enable JSX support
declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}