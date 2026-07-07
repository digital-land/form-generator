// Repeated fields/nodes render as a list of entries whose names carry an index
// ('name-0', 'name-1', ...). Adding an entry clones the last one, bumps the index in
// every name/id so WTForms binds it as the next entry, and blanks the values.
//
// Implementation note - I think this would be better done with an HTTP endpoint returning
// HTML snippets rather then cloning bits of the DOM. Server side build avoids JS and Py
// both needing to know all field types.
function addRepeatedEntry(button) {
  var list = button.closest("[data-repeat-list]");
  var entries = list.querySelectorAll(":scope > [data-repeat-entry]");
  var last = entries[entries.length - 1];

  var baseName = list.dataset.repeatName;
  var oldPrefix = baseName + "-" + (entries.length - 1);
  var newPrefix = baseName + "-" + entries.length;

  function bumpPrefix(value) {
    // only rewrite whole-token matches so e.g. 'phones-1' never rewrites 'phones-10'
    if (value === oldPrefix) {
      return newPrefix;
    }
    if (value.indexOf(oldPrefix + "-") === 0) {
      return newPrefix + value.slice(oldPrefix.length);
    }
    return value;
  }

  var clone = last.cloneNode(true);

  clone.querySelectorAll("[name], [id], [for], [data-repeat-name]").forEach(function (el) {
    ["name", "id", "for", "data-repeat-name"].forEach(function (attr) {
      var value = el.getAttribute(attr);
      if (value) {
        el.setAttribute(attr, bumpPrefix(value));
      }
    });
  });

  // a new entry starts blank
  clone.querySelectorAll("input").forEach(function (input) {
    if (input.type === "checkbox" || input.type === "radio") {
      input.checked = false;
    } else if (input.type !== "hidden") {
      input.value = "";
    }
  });
  clone.querySelectorAll("select, textarea").forEach(function (el) {
    el.value = "";
  });

  // '#n' heading on repeated node entries
  var entryNumber = clone.querySelector(".repeat-entry-number");
  if (entryNumber) {
    entryNumber.textContent = "#" + (entries.length + 1);
  }

  list.insertBefore(clone, button);
}

// On the applications list page each application card carries a profile dropdown. Rewrite the Web form and
// PDF link targets to carry the selected profile so the links behave as normal anchors (e.g.
// open in a new tab).
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".profile-select").forEach(function (select) {
    var card = select.closest(".card");
    if (!card) {
      return;
    }
    var links = card.querySelectorAll(".profile-link");

    function applyProfile() {
      links.forEach(function (link) {
        var url = new URL(link.dataset.baseUrl, window.location.origin);
        url.searchParams.set("profile", select.value);
        link.href = url.toString();
      });
    }

    select.addEventListener("change", applyProfile);
    // set initial targets to match the pre-selected option
    applyProfile();
  });
});
