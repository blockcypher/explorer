function setCoin(coin, label) {
  $('#id_coin_symbol').val(coin);
  $('#search-dropdown-label').html(label);
}
function filterSearch(filter, that) {
  //Update search input
  var sPlaceholder = '';

  switch(filter) {
    case 'address':
      sPlaceholder = '16Fg2yjwrbtC6fZp61EV9mNVKmwCzGasw5';
      break;
    case 'tx_hash':
      sPlaceholder = '2509e5b65ed362557fcf2104e89f3c2430ceecc6a3275556c1b966eb641fe092';
      break;
    case 'block_hash':
      sPlaceholder = '0000000000000000001e847e71b955482dab7228f4849a4659c0cf5cf323f247';
      break;
    case 'block_num':
      sPlaceholder = '330,027';
      break;
    default:
      sPlaceholder = '';
  }

  $('#search_string').val(sPlaceholder);
  $('#search_filter').val(filter);

  $('.search-filter .active').removeClass('active');
  $(that).addClass('active');
}
function satoshis_to_btc(satoshis) {
  // Round to 4 decimal places
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
