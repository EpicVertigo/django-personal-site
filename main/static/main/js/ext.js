window.onload = () => {
  if ($("#success-alert").length) {
    setTimeout(function() {
      $("#success-alert").alert("close");
    }, 3000);
  }
};
