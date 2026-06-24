function repeatedFieldComingSoon() {
  alert("Support for multiple entries on this field is coming soon.");
}

// On the home page each application card carries a profile dropdown. Rewrite the Web form and
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
