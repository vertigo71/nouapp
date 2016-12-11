// converts a Date = d to the format (yyyy-mm-dd)
function convertDate(d) {
  function pad(s) { return (s < 10) ? '0' + s : s; };
  return [ d.getFullYear(),pad(d.getMonth()+1),pad(d.getDate())].join('-');
}
// sets the item to Today
function today(item) {
    document.getElementById(item).value = convertDate(new Date());
}  
// sets the item to today+1 month
function add1month(item) {
    var today = new Date();
    var onemonth = new Date( today.setMonth(today.getMonth() + 1));
    document.getElementById(item).value = convertDate(onemonth);
}
// sets the item to day
function setdate(item, day) {
    var lclday = new Date( day );
    document.getElementById(item).value = convertDate(lclday);
}
