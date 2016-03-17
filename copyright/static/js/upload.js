var fileInput = document.getElementById('fileInput');
var dropzoneWrapper = document.getElementById('dropzoneWrapper');
var previewImg = document.getElementById('previewImg');
var dropzoneDetails = document.getElementById('dropzoneDetails');
var dropzoneName = document.getElementById('dropzoneName');
var dropzoneSize = document.getElementById('dropzoneSize');

if (typeof window.FileReader != 'undefined') { // File API available
  dropzoneWrapper.classList.add('active');
}

if (!detectIE()) {
  dropzoneWrapper.ondragenter = function(e) {
    this.classList.add("drag-hover");
  };
  dropzoneWrapper.ondragover = dropzoneWrapper.ondragenter;
  dropzoneWrapper.ondrop = dropzoneWrapper.ondragenter;

  dropzoneWrapper.ondragend = function(e) {
    this.classList.remove("drag-hover");
  };
  dropzoneWrapper.ondragleave = dropzoneWrapper.ondragend;
} else {
  dropzoneOverlayMessage.innerHTML = "Click to select an image";
}

fileInput.onchange = function(e) {
  // check to make sure we can use File Reader API
  if (typeof window.FileReader === 'undefined')
    return false;

  var reader = new FileReader();
  reader.onload = function(event) {
    previewImg.src = reader.result;
    previewImg.classList.remove('hidden');
    dropzoneDetails.classList.remove('hidden');
  }

  file = e.target.files[0];
  if (file) {
    reader.readAsDataURL(file);
    dropzoneName.innerHTML = file.name;
    dropzoneSize.innerHTML = getFileSizeString(file.size);
  }
}

// takes an integer representing the size of a file in bytes
function getFileSizeString(size) {
  var i = 0;
  var byteUnits = ['bytes', 'KB', 'MB', 'GB'];
  while (size > 1024) {
    size = size / 1024;
    i++;
  }

  return size.toFixed(1) + ' ' + byteUnits[i];
};

function detectIE() {
  var ua = window.navigator.userAgent;

  var msie = ua.indexOf('MSIE ');
  var trident = ua.indexOf('Trident/');
  var edge = ua.indexOf('Edge/');
  if (msie > 0 || trident > 0 || edge > 0) {
     return true;
  }

  // other browser
  return false;
}