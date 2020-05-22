$(document).ready(function() { 
  
    //earnings table
    var table = $('#earnings').DataTable( {
        "searching": false,
        "paging":   false,
        "ordering": false,
        "info":     false,
        dom: 'B<"clear">lfrtip',
        buttons: {
            buttons: [
                { extend: 'excel',
                text: 'Save Excel File',
                filename: 'earnings',        
                className: 'btn btn-primary btn-lg' }
            ]
        }

    });

    //handle form and results
    $('#period').submit(function(e) {
        e.preventDefault();
        $("#results").fadeOut();
        $("#cboe_results").fadeOut();
        $("#submit_button").attr('disabled', true);
        $("#submit_button").html("Waiting ...");
        var post_url = $("#period").attr("action"); //get form action url
        var request_method = $("#period").attr("method"); //get form GET/POST method
        var form_data = $("#period").serialize(); //Encode form elements for submission

        $.ajax({
            url : post_url,
            type: request_method,
            data : form_data,
            datatype: 'json',
            success: function(response) {
                if (typeof(response) == "string") {
                    $("#alert_danger").html("<strong>Oh snap!</strong>" + " " + response + "!" + " Wait a minute and try submitting again");
                    $("#alerts").fadeIn();
                    $("#submit_button").html("Search")
                    $("#submit_button").attr('disabled', false)
                    $("#period")[0].reset()

                }
                else {
                    table.rows.add(response).draw();
                    $("tr").addClass("table-dark");
                    $("#results").fadeIn();
                    $("#submit_button").html("Search")
                    $("#submit_button").attr('disabled', false)
                    $("#period")[0].reset()
                }

            }
        })
        
    })
    
});

//get cboe datas
function get_cboe_datas() {
    $("#crossreferencebutton").html("Waiting ...");
    $("#crossreferencebutton").attr('disabled', true)
    $.ajax({
        url: '/crossreference',
        type: 'GET',
        datatype: 'json',
        success: function(response) {
            if (typeof(response) == "string") {
                $("#alert_danger").html("<strong>Oh snap!</strong>" + " " + response + "!" + " Wait a minute and try submitting again");
                $("#alerts").fadeIn();
                $("#crossreferencebutton").html('Cross Reference');
                $("#crossreferencebutton").attr('disabled', false);
            }
            else {
               //cboe table
                var table_ = $('#cboe_datas').DataTable( {
                    "destroy": true,
                    "searching": false,
                    "paging":   false,
                    "ordering": false,
                    "info":     false,
                    buttons: {
                        buttons: [
                            { extend: 'excel',
                            text: 'Save Excel File',
                            filename: 'datas',        
                            className: 'btn btn-primary btn-lg' }
                        ]
                    }
                });

                table_.buttons().container().insertBefore("#cboe_datas");
                table_.rows.add(response).draw();
                $("tr").addClass("table-dark");
                $("#cboe_results").fadeIn();
                $("#crossreferencebutton").html('Cross Reference');
                $("#crossreferencebutton").attr('disabled', false)
            }
            
        }
    })
}