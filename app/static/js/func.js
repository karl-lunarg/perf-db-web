// some jquery methods to interact with index.html
$(document).ready(function() {
    // example queries
    var select_all_query = "SELECT * FROM results;";
    var select_baseline_query = "SELECT * FROM results WHERE baseline=1;";
    var select_latest_query = "SELECT *, max(date) AS latest FROM results GROUP BY tracename;";
    var show_schema_query = "SELECT SQL FROM sqlite_master WHERE name = 'results'"

    var modal = document.getElementById("myModal");
    var modal_content = document.getElementById("modal_content");

    var span = document.getElementsByClassName("close")[0];

    $("#select_all_query").click(function(event) {
        $('#queryArea').val(select_all_query);
    });

    $("#select_baseline_query").click(function(event) {
        $('#queryArea').val(select_baseline_query);
    });

    $("#select_latest_query").click(function(event) {
        $('#queryArea').val(select_latest_query);
    });

    $("#show_schema_query").click(function(event) {
        $('#queryArea').val(show_schema_query);
    });

    // call the REST API and show results
    $("#run_query").click(function(event) {
        call = "./run?query=" + escape($('#queryArea').val())
        $.get(call, function(data, status){
            var jsonObj = JSON.parse(data);
            var jsonPretty = JSON.stringify(jsonObj, null, '\t');

            modal.style.display = "block";
            $("#modal_content").text(jsonPretty);
        });
    });

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
});



