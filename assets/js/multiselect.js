import $ from 'jquery';

// Export jQuery for external usage
window.jQuery = window.$ = $; // eslint-disable-line no-multi-assign

// -----------------------------------------------------------------------------
// Main application
// -----------------------------------------------------------------------------

$(() => {
  $('.limited-multiselect').each((index, elem) => {
    const that = $(elem);

    // bloque sur la valeur min
    if (that.children(':selected').length <= that.data('min')) {
      that.children(':selected').addClass('disabled', '');
    }

    // bloque sur la valeur max
    if (that.children(':selected').length >= that.data('max')) {
      that.children(':not(:selected)').addClass('disabled', '');
    }

    that.multiSelect({
      keepOrder: true,
      afterSelect() {
        // bloque sur la valeur max
        if (that.children(':selected').length >= that.data('max')) {
          that.children(':not(:selected)').addClass('disabled', '');
        }

        // libere sur la valeur min
        if (that.children(':selected').length > that.data('min')) {
          that.children(':selected').removeClass('disabled');
        }

        that.multiSelect('refresh');
      },
      afterDeselect() {
        // bloque sur la valeur min
        if (that.children(':selected').length <= that.data('min')) {
          that.children(':selected').addClass('disabled');
        }

        // libere sur la valeur max
        if (that.children(':selected').length < that.data('max')) {
          that.children(':not(:selected)').removeClass('disabled');
        }

        that.multiSelect('refresh');
      }
    });
  });
});
