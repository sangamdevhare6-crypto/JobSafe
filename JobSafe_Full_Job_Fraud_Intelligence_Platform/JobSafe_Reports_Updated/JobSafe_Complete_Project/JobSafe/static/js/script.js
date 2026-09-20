document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       STAT COUNTER ANIMATION
    ========================= */

    document.querySelectorAll(".stat b").forEach(el => {

        const target = parseInt(el.textContent) || 0;
        let n = 0;

        const timer = setInterval(() => {

            n += Math.max(1, Math.ceil(target / 18));

            if (n >= target) {
                n = target;
                clearInterval(timer);
            }

            el.textContent = n;

        }, 35);

    });


    /* =========================
       GLASS CARD 3D HOVER
    ========================= */

    document.querySelectorAll(".glass").forEach(card => {

        card.addEventListener("mousemove", event => {

            const rect = card.getBoundingClientRect();

            if (!rect.width || !rect.height) {
                return;
            }

            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;

            const rotateX =
                ((y / rect.height) - 0.5) * -5;

            const rotateY =
                ((x / rect.width) - 0.5) * 5;

            card.style.transform =
                `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-3px)`;

        });

        card.addEventListener("mouseleave", () => {

            card.style.transform =
                "perspective(900px) rotateX(0deg) rotateY(0deg) translateY(0)";

        });

    });


    /* =========================
       COMPANY SEARCH
    ========================= */

    const input =
        document.getElementById("companySearchInput");

    const button =
        document.getElementById("companySearchButton");

    const resultsBox =
        document.getElementById("companySearchResults");


    if (!input || !button || !resultsBox) {
        return;
    }


    /* =========================
       MOVE DROPDOWN TO BODY
    ========================= */

    if (resultsBox.parentElement !== document.body) {
        document.body.appendChild(resultsBox);
    }


    /* =========================
       FORCE DROPDOWN POSITION
    ========================= */

    resultsBox.style.position = "fixed";
    resultsBox.style.zIndex = "2147483647";
    resultsBox.style.display = "none";
    resultsBox.style.pointerEvents = "auto";


    let searchTimer = null;
    let searchController = null;


    /* =========================
       ESCAPE HTML
    ========================= */

    function escapeHtml(value) {

        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");

    }


    /* =========================
       POSITION DROPDOWN
    ========================= */

    function positionResults() {

        const rect =
            input.getBoundingClientRect();


        if (!rect.width || !rect.height) {
            return;
        }


        const viewportWidth =
            window.innerWidth;

        const viewportHeight =
            window.innerHeight;


        const gap = 8;


        let left =
            rect.left;

        let top =
            rect.bottom + gap;


        let width =
            Math.max(rect.width, 360);


        const maxWidth =
            viewportWidth - 30;


        if (width > maxWidth) {
            width = maxWidth;
        }


        if (left + width > viewportWidth - 15) {

            left =
                viewportWidth - width - 15;

        }


        if (left < 15) {
            left = 15;
        }


        const dropdownHeight =
            Math.min(
                resultsBox.scrollHeight || 430,
                430
            );


        if (
            top + dropdownHeight >
            viewportHeight - 15
        ) {

            const aboveTop =
                rect.top - dropdownHeight - gap;


            if (aboveTop >= 15) {
                top = aboveTop;
            }

        }


        resultsBox.style.left =
            `${Math.round(left)}px`;

        resultsBox.style.top =
            `${Math.round(top)}px`;

        resultsBox.style.width =
            `${Math.round(width)}px`;

        resultsBox.style.maxWidth =
            "calc(100vw - 30px)";

    }


    /* =========================
       SHOW DROPDOWN
    ========================= */

    function showResults() {

        positionResults();

        resultsBox.style.display = "block";

        resultsBox.classList.add("active");

    }


    /* =========================
       HIDE DROPDOWN
    ========================= */

    function hideResults() {

        resultsBox.classList.remove("active");

        resultsBox.style.display = "none";

        resultsBox.innerHTML = "";

    }


    /* =========================
       LOADING
    ========================= */

    function showLoading() {

        resultsBox.innerHTML = `
            <div class="search-loading">
                🔎 Searching companies...
            </div>
        `;

        showResults();

    }


    /* =========================
       EMPTY RESULT
    ========================= */

    function showEmpty(query) {

        resultsBox.innerHTML = `
            <div class="search-empty">
                No company found for
                "<strong>${escapeHtml(query)}</strong>"
            </div>
        `;

        showResults();

    }


    /* =========================
       ERROR
    ========================= */

    function showError() {

        resultsBox.innerHTML = `
            <div class="search-empty">
                ⚠️ Unable to search companies.
                <br>
                Please try again.
            </div>
        `;

        showResults();

    }


    /* =========================
       SEARCH COMPANIES
    ========================= */

    async function searchCompanies() {

        const query =
            input.value.trim();


        if (query.length < 2) {

            hideResults();

            return;

        }


        if (searchController) {
            searchController.abort();
        }


        searchController =
            new AbortController();


        showLoading();


        try {

            const response =
                await fetch(
                    `/api/company-search/?q=${encodeURIComponent(query)}`,
                    {
                        method: "GET",
                        headers: {
                            "Accept": "application/json"
                        },
                        signal: searchController.signal
                    }
                );


            if (!response.ok) {
                throw new Error(
                    `HTTP ${response.status}`
                );
            }


            const data =
                await response.json();


            if (
                !data ||
                !data.success ||
                !Array.isArray(data.results) ||
                data.results.length === 0
            ) {

                showEmpty(query);

                return;

            }


            resultsBox.innerHTML = "";


            data.results.forEach(company => {

                const item =
                    document.createElement("div");


                item.className =
                    "company-result-item";


                const icon =
                    document.createElement("div");

                icon.className =
                    "company-result-icon";

                icon.textContent =
                    "🏢";


                const info =
                    document.createElement("div");

                info.className =
                    "company-result-info";


                const name =
                    document.createElement("strong");

                name.textContent =
                    company.name ||
                    "Unknown Company";


                const description =
                    document.createElement("small");

                description.textContent =
                    company.description ||
                    "Company information available";


                info.appendChild(name);
                info.appendChild(description);


                item.appendChild(icon);
                item.appendChild(info);


                item.addEventListener("click", event => {

                    event.stopPropagation();


                    const companyName =
                        company.name ||
                        "Unknown Company";


                    window.location.href =
                        `/company-check/?company=${encodeURIComponent(companyName)}`;

                });


                resultsBox.appendChild(item);

            });


            showResults();


        } catch (error) {

            if (error.name === "AbortError") {
                return;
            }


            console.error(
                "Company Search Error:",
                error
            );


            showError();

        }

    }


    /* =========================
       SEARCH WHILE TYPING
    ========================= */

    input.addEventListener("input", () => {

        clearTimeout(searchTimer);


        const query =
            input.value.trim();


        if (query.length < 2) {

            hideResults();

            return;

        }


        searchTimer =
            setTimeout(() => {

                searchCompanies();

            }, 350);

    });


    /* =========================
       SEARCH BUTTON
    ========================= */

    button.addEventListener("click", event => {

        event.preventDefault();
        event.stopPropagation();


        clearTimeout(searchTimer);

        searchCompanies();

    });


    /* =========================
       ENTER + ESCAPE
    ========================= */

    input.addEventListener("keydown", event => {

        if (event.key === "Enter") {

            event.preventDefault();

            clearTimeout(searchTimer);

            searchCompanies();

        }


        if (event.key === "Escape") {

            hideResults();

            input.blur();

        }

    });


    /* =========================
       CLICK INPUT
    ========================= */

    input.addEventListener("focus", () => {

        if (
            input.value.trim().length >= 2 &&
            resultsBox.innerHTML.trim() !== ""
        ) {

            showResults();

        }

    });


    /* =========================
       OUTSIDE CLICK
    ========================= */

    document.addEventListener("click", event => {

        const clickedSearchBox =
            event.target.closest(
                ".company-search-box"
            );


        const clickedResults =
            resultsBox.contains(event.target);


        if (
            !clickedSearchBox &&
            !clickedResults
        ) {

            hideResults();

        }

    });


    /* =========================
       RESIZE
    ========================= */

    window.addEventListener(
        "resize",
        () => {

            if (
                resultsBox.style.display === "block"
            ) {

                positionResults();

            }

        }
    );


    /* =========================
       SCROLL
    ========================= */

    window.addEventListener(
        "scroll",
        () => {

            if (
                resultsBox.style.display === "block"
            ) {

                positionResults();

            }

        },
        true
    );


});