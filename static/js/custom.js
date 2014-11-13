function setCoin(coin){
  $('#coin_symbol').val(coin);
}

function satoshis_to_btc(satoshis) {
  // Round to 4 decimal places
  var btc = satoshis/(Math.pow(10,8));
  return Math.round(btc*10000)/10000;
}

function convert_time_to_seconds_ago(epoch) {
  return (Date.now() - Date.parse(epoch))/1000;
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
