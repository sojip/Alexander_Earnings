$(document).ready(function() { 

    
    //celery 
    $("#period").submit(function(e){
        e.preventDefault();
        start_long_task();
    })

//     //handle form and results
//     $('#period').submit(function(e) {
//         e.preventDefault();
//         $("#submit_button").attr('disabled', true);
//         $("#submit_button").html("Waiting ...");
//         var post_url = $("#period").attr("action"); //get form action url
//         var request_method = $("#period").attr("method"); //get form GET/POST method
//         var form_data = $("#period").serialize(); //Encode form elements for submission

//         // add task status elements 
//         div = $('<div class="progress"><div></div><div>0%</div><div>...</div><div>&nbsp;</div></div><hr>');
//         $('#progress').append(div);

//         // create a progress bar
//         var nanobar = new Nanobar({
//             bg: '#44f',
//             target: div[0].childNodes[0]
//         });

//         $.ajax({
//             url : post_url,
//             type: request_method,
//             data : form_data,
//             datatype: 'json',
//             success: function(response) {
//                 // if (typeof(response) == "string") {
//                 //     $("#alert_danger").html("<strong>Oh snap!</strong>" + " " + response + "!" + " Wait a minute and try submitting again");
//                 //     $("#alerts").fadeIn();
//                 //     $("#submit_button").html("Search")
//                 //     $("#submit_button").attr('disabled', false)
//                 //     $("#period")[0].reset()

//                 // }
//                 // else {
//                 //     table.rows.add(response).draw();
//                 //     $("tr").addClass("table-dark");
//                 //     $("#results").fadeIn();
//                 //     $("#submit_button").html("Search")
//                 //     $("#submit_button").attr('disabled', false)
//                 //     $("#period")[0].reset()
//                 // }

//             },
//             error: function() {
//                 alert('Unexpected error');
//             }
//         })
        
//     })
    
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


//celery
function start_long_task() {
    // add task status elements 
    div = $('<div class="progress"><div></div><div>0%</div><div>...</div><div>&nbsp;</div></div><hr>');
    $('#progress').append(div);

    // create a progress bar
    var nanobar = new Nanobar({
        bg: '#44f',
        target: div[0].childNodes[0]
    });

    var post_url = $("#period").attr("action"); //get form action url
    var request_method = $("#period").attr("method"); //get form GET/POST method
    var form_data = $("#period").serialize(); //Encode form elements for submission

    // send ajax POST request to start background job
    $.ajax({
        type: request_method,
        url: post_url,
        data: form_data,
        success: function(data, status, request) {
            status_url = request.getResponseHeader('Location');
            update_progress(status_url, nanobar, div[0]);
        },
        error: function() {
            alert('Unexpected error');
        }
    });
}




function update_progress(status_url, nanobar, status_div) {
    // send GET request to status URL
    $.getJSON(status_url, function(data) {
        // update UI
        if(Number.isNaN(parseInt(data['current'], 10) * 100 / parseInt(data['total'], 10)) == true) {
            percent = 0;      
        } else {
            percent = parseInt(data['current'], 10) * 100 / parseInt(data['total'], 10);
        }
        nanobar.go(percent);
        $(status_div.childNodes[1]).text(percent + '%');
        $(status_div.childNodes[2]).text(data['status']);
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                // show result in earnings table

                // if Datable is already initialise
                if ( $.fn.dataTable.isDataTable( '#earnings' ) ) {
                    var table = $('#earnings').DataTable();
                    var rows = $("#earnings").find("tr:gt(0)");
                    for (i = 0; i < rows.length; i++) {
                        table.row(rows[i]).remove().draw();
                    }
                    
                }
                else {
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

                }
                table.rows.add(data['result']).draw();
                $("tr").addClass("table-dark");
                $("#results").fadeIn();
            }
            else {
                // something unexpected happened
                $(status_div.childNodes[3]).text('Result: ' + data['state']);
            }
        }
        else {
            // rerun in 2 seconds
            setTimeout(function() {
                update_progress(status_url, nanobar, status_div);
            }, 2000);
        }
    });
}