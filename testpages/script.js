function fillcontent () {
  var element = document.getElementsByClassName('autofill')[0]
  element.innerHTML = 'If you can read this line JavaScript worked.'
}

window.onload = fillcontent
