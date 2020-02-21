import $ from 'jquery';

import './vendor/bootstrap';

// Export jQuery for external usage
window.jQuery = window.$ = $; // eslint-disable-line no-multi-assign

// -----------------------------------------------------------------------------
// Main application
// -----------------------------------------------------------------------------

$(() => {
  $('.no-js').removeClass('no-js');

  // Initialize Popover and Tooltip on the whole page
  $('[data-toggle="popover"]').popover();
  $('[data-toggle="tooltip"]').tooltip();
});
