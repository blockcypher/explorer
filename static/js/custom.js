function setCoin(coin, label) {
  $('#id_coin_symbol').val(coin);
  $('#search-dropdown-label').html(label);
  // This only affects the homepage
  $('.search-filter .active').removeClass('active');
}

function satoshis_to_btc_full(satoshis) {
  return satoshis/(Math.pow(10,8));
}

function satoshis_to_btc_rounding(satoshis) {
  // Round to 4 decimal places
  // Strange name because of namespacing issue
  var btc = satoshis/(Math.pow(10,8));
  return Math.round(btc*10000)/10000;
}

function convert_time_to_seconds_ago(time) {
  return (Date.now() - Date.parse(time))/1000;
}

function convert_epoch_to_seconds_ago(epoch) {
  return Math.round((Date.now() - new Date(epoch*1000))/1000, 0);
}

function format_seconds_ago(seconds_ago) {
  if( seconds_ago < 60) {
    return  '<1 min ago';
  } else if (seconds_ago < 120) {
    return '<2 mins ago';
  } else if (seconds_ago < 180) {
    return '<3 mins ago';
  } else if (seconds_ago < 240) {
    return '<4 mins ago';
  } else if (seconds_ago < 300) {
    return '<5 mins ago';
  } else if (seconds_ago < 600) {
    return '<10 mins ago';
  } else {
    return '>5 minutes ago';
  }
}

function fetch_metadata(coin_symbol, identifier_type, identifier) {
  $.ajax({
    type: 'get',
    url: '/metadata/' + coin_symbol + '/' + identifier_type + '/' + identifier + '/',
    success: function (data) {
      console.log('fetch_metadata API Call Success');
      console.log('data:');
      console.log(data);

      var is_empty = true;
      for (var key in data.metadata) {
        if (data.metadata.hasOwnProperty(key)) {
          $('#metadata-tbody').append('<tr><td><pre>' + key + '</pre></td><td><pre>' + data.metadata[key] + '</pre></td></tr>');
          is_empty = false;
        }
      }

      if (is_empty === true) {
        $('#metadata-table').hide()
        $('#metadata-empty-notice').show()
      }

      $('#metadata-section').fadeIn()

    },
    error: function(data) {
      console.log('fetch_metadata API Call Failure');
    }
  });
}
