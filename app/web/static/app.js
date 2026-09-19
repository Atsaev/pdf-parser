(function () {
  "use strict";

  function bind(zone) {
    var input = zone.querySelector('input[type="file"]');
    var label = zone.querySelector("[data-filename]");
    if (!input || !label) return;

    var empty = zone.dataset.empty || "";

    function sync() {
      var file = input.files && input.files[0];
      label.textContent = file ? file.name : empty;
      zone.classList.toggle("has-file", Boolean(file));
    }

    function stop(event) {
      event.preventDefault();
      event.stopPropagation();
    }

    ["dragenter", "dragover"].forEach(function (type) {
      zone.addEventListener(type, function (event) {
        stop(event);
        zone.classList.add("dragging");
      });
    });

    ["dragleave", "dragend"].forEach(function (type) {
      zone.addEventListener(type, function (event) {
        stop(event);
        zone.classList.remove("dragging");
      });
    });

    zone.addEventListener("drop", function (event) {
      stop(event);
      zone.classList.remove("dragging");
      if (event.dataTransfer && event.dataTransfer.files.length) {
        input.files = event.dataTransfer.files;
        sync();
      }
    });

    input.addEventListener("change", sync);
    sync();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-dropzone]").forEach(bind);
  });
})();
