var CsvToHtmlTable = CsvToHtmlTable || {};

CsvToHtmlTable = {
    init: function (options) {
        options = options || {};
        var csv_path = options.csv_path || "";
        var el = options.element || "table-container";
        var allow_download = options.allow_download || false;
        var download_el = options.download_button || ""; // Specify the download button's container ID.
        var csv_options = options.csv_options || {};
        var datatables_options = options.datatables_options || {
            paging: false,
            initComplete: function(settings, json) {
                var dataTableWrapper = $(`#${settings.sTableId}_wrapper`);
                var searchInput = dataTableWrapper.find('.dataTables_filter').detach();
                $('#search-container').append(searchInput);
                searchInput.find('input').addClass('form-control').attr('placeholder', 'Search...');
                searchInput.find('label').contents().unwrap();

                var infoLabel = dataTableWrapper.find('.dataTables_info').detach();
                $('#info-container').append(infoLabel);
            }
        };
        var custom_formatting = options.custom_formatting || [];
        var customTemplates = {};

        $.each(custom_formatting, function (i, v) {
            var colIdx = v[0];
            var func = v[1];
            customTemplates[colIdx] = func;
        });

        var $table = $("<table class='table table-striped table-condensed' id='" + el + "-table'></table>");
        var $containerElement = $("#" + el);
        $containerElement.empty().append($table);

        $.when($.get(csv_path)).then(function (data) {
            var csvData = $.csv.toArrays(data, csv_options);
            var $tableHead = $("<thead></thead>");
            var csvHeaderRow = csvData[0];
            var $tableHeadRow = $("<tr></tr>");
            for (var headerIdx = 0; headerIdx < csvHeaderRow.length; headerIdx++) {
                $tableHeadRow.append($("<th></th>").text(csvHeaderRow[headerIdx]));
            }
            $tableHead.append($tableHeadRow);
            $table.append($tableHead);
            var $tableBody = $("<tbody></tbody>");

            for (var rowIdx = 1; rowIdx < csvData.length; rowIdx++) {
                var $tableBodyRow = $("<tr></tr>");
                for (var colIdx = 0; colIdx < csvData[rowIdx].length; colIdx++) {
                    var $tableBodyRowTd = $("<td></td>");
                    var cellTemplateFunc = customTemplates[colIdx];
                    if (cellTemplateFunc) {
                        $tableBodyRowTd.html(cellTemplateFunc(csvData[rowIdx][colIdx]));
                    } else {
                        $tableBodyRowTd.text(csvData[rowIdx][colIdx]);
                    }
                    $tableBodyRow.append($tableBodyRowTd);
                }
                $tableBody.append($tableBodyRow);
            }
            $table.append($tableBody);

            $table.DataTable(datatables_options);

            if (allow_download) {
                var $downloadButton = $("<a class='btn btn-info' href='" + csv_path + "' download><i class='glyphicon glyphicon-download'></i> Download CSV</a>");
                $("#" + download_el).append($downloadButton);
            }
        });
    }
};

// Additional functions for custom formatting if needed
function format_link(link) {
    return link ? "<a href='https://hpo.jax.org/app/browse/term/" + link + "' target='_blank'>" + link + "</a>" : "";
}

function disease_link(link) {
    if (!link) return "";
    const items = link.split("|").map(item => item.trim());
    const prefixes = {
        "ORPHA": "https://www.orpha.net/en/disease/detail/",
        "OMIM": "https://www.omim.org/entry/"
    };
    const htmlLinks = items.map(item => {
        const parts = item.split(":");
        const prefix = parts[0].trim();
        const id = parts[1].trim();
        const baseUrl = prefixes[prefix];
        return baseUrl ? `<a href='${baseUrl + id}' target='_blank'>${item}</a>` : item;
    });
    return htmlLinks.join("<br>");
}

function gene_link(genes) {
    // Check if the input is null, undefined, or an empty string
    if (!genes) return "";

    // Split the input string by '|' to separate each gene entry
    const geneList = genes.split("|").map(gene => gene.trim());

    // Generate HTML links for each gene entry
    const htmlLinks = geneList.map(gene => {
        // Split each gene entry into prefix, geneId, and geneName by ':'
        const parts = gene.split(":");
        if (parts.length !== 3) return ''; // Skip malformed entries
        const geneId = parts[1].trim();
        const geneName = parts[2].trim();

        // Return an HTML anchor element with the URL pointing to the geneId
        // and the link text displaying the geneName
        return `<a href='https://www.ncbi.nlm.nih.gov/gene/${geneId}' target='_blank'>${geneName}</a>`;
    });

    // Join the HTML links with line breaks (<br>) to separate each link
    return htmlLinks.join("<br>");
}
//function gene_link(genes) {
//    if (!genes) return "";
//    const geneList = genes.split("|").map(gene => gene.trim());
//    const htmlLinks = geneList.map(gene => `<a href='https://www.ncbi.nlm.nih.gov/gene/${gene}' target='_blank'>${gene}</a>`);
//    return htmlLinks.join("<br>");
//}

function ref_link(ref) {
    if (!ref) return "";
    const refList = ref.split("|").map(ref => ref.trim());
    return refList.join("<br>-<br>");
}

function syn_link(syn) {
    if (!syn) return "";
    const synList = syn.split("|").map(syn => syn.trim());
    return synList.join("<br>-<br>");
}