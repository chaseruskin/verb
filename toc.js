// Populate the sidebar
//
// This is a script, and not included directly in the page, to control the total size of the book.
// The TOC contains an entry for each page, so if each page includes a copy of the TOC,
// the total size of the page becomes O(n**2).
class MDBookSidebarScrollbox extends HTMLElement {
    constructor() {
        super();
    }
    connectedCallback() {
        this.innerHTML = '<ol class="chapter"><li class="chapter-item expanded affix "><a href="index.html">Introduction</a></li><li class="chapter-item expanded "><a href="starting.md/starting.html"><strong aria-hidden="true">1.</strong> Getting Started</a></li><li><ol class="section"><li class="chapter-item expanded "><a href="starting/motivation.html"><strong aria-hidden="true">1.1.</strong> Motivation</a></li><li class="chapter-item expanded "><a href="starting/installing.html"><strong aria-hidden="true">1.2.</strong> Installing</a></li></ol></li><li class="chapter-item expanded "><a href="tutorials/tutorials.html"><strong aria-hidden="true">2.</strong> Tutorials</a></li><li class="chapter-item expanded "><a href="user/user.html"><strong aria-hidden="true">3.</strong> User Guide</a></li><li class="chapter-item expanded "><a href="topic/topic.html"><strong aria-hidden="true">4.</strong> Topic Guide</a></li><li><ol class="section"><li class="chapter-item expanded "><a href="topic/overview.html"><strong aria-hidden="true">4.1.</strong> Overview</a></li><li class="chapter-item expanded "><a href="topic/vectors.html"><strong aria-hidden="true">4.2.</strong> Test Vectors</a></li><li class="chapter-item expanded "><a href="topic/coverage.html"><strong aria-hidden="true">4.3.</strong> Coverage</a></li><li class="chapter-item expanded "><a href="topic/events.html"><strong aria-hidden="true">4.4.</strong> Events</a></li></ol></li><li class="chapter-item expanded "><a href="reference/reference.html"><strong aria-hidden="true">5.</strong> Reference</a></li><li><ol class="section"><li class="chapter-item expanded "><a href="reference/api-python.html"><strong aria-hidden="true">5.1.</strong> Python API</a></li><li class="chapter-item expanded "><a href="reference/api-systemverilog.html"><strong aria-hidden="true">5.2.</strong> SystemVerilog API</a></li><li class="chapter-item expanded "><a href="reference/api-vhdl.html"><strong aria-hidden="true">5.3.</strong> VHDL API</a></li><li class="chapter-item expanded "><a href="reference/environment.html"><strong aria-hidden="true">5.4.</strong> Environment Variables</a></li></ol></li><li class="chapter-item expanded "><a href="glossary.html"><strong aria-hidden="true">6.</strong> Appendix: Glossary</a></li></ol>';
        // Set the current, active page, and reveal it if it's hidden
        let current_page = document.location.href.toString().split("#")[0].split("?")[0];
        if (current_page.endsWith("/")) {
            current_page += "index.html";
        }
        var links = Array.prototype.slice.call(this.querySelectorAll("a"));
        var l = links.length;
        for (var i = 0; i < l; ++i) {
            var link = links[i];
            var href = link.getAttribute("href");
            if (href && !href.startsWith("#") && !/^(?:[a-z+]+:)?\/\//.test(href)) {
                link.href = path_to_root + href;
            }
            // The "index" page is supposed to alias the first chapter in the book.
            if (link.href === current_page || (i === 0 && path_to_root === "" && current_page.endsWith("/index.html"))) {
                link.classList.add("active");
                var parent = link.parentElement;
                if (parent && parent.classList.contains("chapter-item")) {
                    parent.classList.add("expanded");
                }
                while (parent) {
                    if (parent.tagName === "LI" && parent.previousElementSibling) {
                        if (parent.previousElementSibling.classList.contains("chapter-item")) {
                            parent.previousElementSibling.classList.add("expanded");
                        }
                    }
                    parent = parent.parentElement;
                }
            }
        }
        // Track and set sidebar scroll position
        this.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                sessionStorage.setItem('sidebar-scroll', this.scrollTop);
            }
        }, { passive: true });
        var sidebarScrollTop = sessionStorage.getItem('sidebar-scroll');
        sessionStorage.removeItem('sidebar-scroll');
        if (sidebarScrollTop) {
            // preserve sidebar scroll position when navigating via links within sidebar
            this.scrollTop = sidebarScrollTop;
        } else {
            // scroll sidebar to current active section when navigating via "next/previous chapter" buttons
            var activeSection = document.querySelector('#sidebar .active');
            if (activeSection) {
                activeSection.scrollIntoView({ block: 'center' });
            }
        }
        // Toggle buttons
        var sidebarAnchorToggles = document.querySelectorAll('#sidebar a.toggle');
        function toggleSection(ev) {
            ev.currentTarget.parentElement.classList.toggle('expanded');
        }
        Array.from(sidebarAnchorToggles).forEach(function (el) {
            el.addEventListener('click', toggleSection);
        });
    }
}
window.customElements.define("mdbook-sidebar-scrollbox", MDBookSidebarScrollbox);
