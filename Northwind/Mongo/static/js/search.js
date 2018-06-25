// What we will store our 'cart' in
var cart = [];

function add_to_cart(id, name) {
  // Add 1 quantity of an item to your cart. The name is included
  // so we don't have to ask the database (which is now remote).

  // First check if the item is already in the cart, if so, add 1 to the quanity.
  for (var i = 0; i < cart.length; i++) {
    if (cart[i].id == id) {
      // This is kind of ugly, but the id tag for the number of a product remaining
      // is set to the products's ID followed by '_left'. So by using this selector
      // we can get that number without having to query the database either.
      // e.g., an item with ID of 4 would be: <span id="4_left">26</span>
      // meaning there are 26 of the item with ID 4 left in stock.
      var max = parseInt($('#'+id+'_left').html());

      // As long as there are items left to take.
      if (cart[i].quantity < max) {
        cart[i].quantity += 1;
        update_cart();
      }
      return;
    }
  }
  // If it isn't anywhere in the cart, create a new element and add it.
  cart.push({id: id, quantity: 1, name: name});
  update_cart();
}

function update_results(val) {
  $.post('/search', {data: val}, function(response) {
    // Clear out previous results.
    $('#results').empty();

    // Add in the html we got back from the server.
    $('#results').append(response);
  });
}

function update_cart() {
  // Pretty much the same as update_results but this time it updates the cart.
  // Also NOTE: JSON.stringify is used here because cart is an array which is
  // not supported with this function.
  $.post('/render_cart', JSON.stringify(cart), function(response) {
    $('#cart').empty();
    $('#cart').append(response);
  });
}

function convert_to_cs() {
  if (cart.length == 0) return "";
  var str = "/";
  for (var i = 0; i < cart.length; i++) {
    str += cart[i].id + ",";
    str += cart[i].quantity;
    if (i < cart.length - 1) {
      str += ",";
    }
  }
  return str;
}

$(document).ready(function() {
  // Bind a function to a keyup event in the input field (basically every time the user types a letter)
  $('#search_input').on('keyup', function() {
    // Checks to make sure the user actually typed something
    if ($(this).val() != "") {
      update_results($(this).val());
    }
  });

  $('#place_order_button').on('click', function() {
    window.location.replace("/order" + convert_to_cs());
  });
});
