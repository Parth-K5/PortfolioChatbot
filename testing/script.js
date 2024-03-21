let iframeVisible = false;

function toggleIframe() {
  const iframeContainer = document.getElementById('iframeContainer');
  iframeVisible = !iframeVisible;
  iframeContainer.style.display = iframeVisible ? 'block' : 'none';
}

function closeIframe() {
  const iframeContainer = document.getElementById('iframeContainer');
  iframeVisible = false;
  iframeContainer.style.display = 'none';
}