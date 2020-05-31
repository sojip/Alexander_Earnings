$(document).ready(function() {

    // add search task status elements 
    div = $('<div class="progress_container"><div></div><div>0%</div><hr>');
    $('#progress').append(div);

    div_ = $('<div class="progress_container"><div></div><div>0%</div><hr>');
    $('#progress_2').append(div_);



    // create search progress bar
    var nanobar = new Nanobar({
        bg: '#5cb85c',
        target: div[0].childNodes[0]
    });


    //Always delete previous alert when showing new one
    $.noty.defaults.killer = true;
  
    //handle period form
    $("#period").submit(function(e){
        e.preventDefault();
        $("#results").fadeOut();
        $("#cboe_results").fadeOut();
        $("#progress_bar").fadeOut();
        $("#progress_bar_2").fadeOut();
        $("#noty").noty({
            text: 'Submitted!',
            layout: 'topCenter',
            timeout: 5000,
            closeWith: ['click', 'hover'],
            type: 'success'
            });
        start_search(nanobar);
    })
});


function start_search(nanobar) {
    
    var post_url = $("#period").attr("action"); //get form action url
    var request_method = $("#period").attr("method"); //get form GET/POST method
    var form_data = $("#period").serialize(); //Encode form elements for submission
    $("#period")[0].reset()
    // send ajax POST request to start background job
    $.ajax({
        type: request_method,
        url: post_url,
        data: form_data,
        success: function(data, status, request) {
            status_url = request.getResponseHeader('Location');
            update_search_progress(status_url, nanobar, div[0]);
        },
        error: function() {
            $("#noty").noty({
                text: 'Unexpected Error!',
                layout: 'topCenter',
                timeout: 5000,
                closeWith: ['click', 'hover'],
                type: 'error'
                });
        }
    });
}




function update_search_progress(status_url, nanobar, status_div) {
    $("#progress_bar").fadeIn();
    // send GET request to status URL
    $.getJSON(status_url, function(data) {
        // update UI
        if(Number.isNaN(parseInt(data['current'], 10) * 100 / parseInt(data['total'], 10)) == true) {
            percent = 0;      
        } else {
            percent = Math.floor(parseInt(data['current'], 10) * 100 / parseInt(data['total'], 10));
        }
        nanobar.go(percent);
        $(status_div.childNodes[1]).text(percent + '%');
        $(status_div.childNodes[2]).text(data['message']);
        if (data['state'] == 'SUCCESS') {
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
                $("#noty").noty({
                    text: data['state'],
                    layout: 'topCenter',
                    timeout: 5000,
                    closeWith: ['click', 'hover'],
                    type: 'error'
                    });
                $("#progress_bar").fadeOut();
                
            }
        }
        else {
            // rerun in 2 seconds
            setTimeout(function() {
                update_search_progress(status_url, nanobar, status_div);
            }, 2000);
        }
    });
}


//get cboe datas
function start_reference() {

    $("#cboe_results").fadeOut();
    //Get tickers form the earnings tables
    var table = $('#earnings').DataTable();
    my_list = table
    .columns( 0 )
    .data()
    .eq( 0 )      // Reduce the 2D array into a 1D array of data
    .unique()   // Reduce to unique values
    .join("<br>")

    $.ajax({
        type: 'POST',
        url: '/crossreference',
        data: {'tickers': my_list},
        success: function(data, status, request) {
            status_url = request.getResponseHeader('Location');
            update_reference_progress(status_url, div_[0]);
        },
        error: function() {
            $("#noty").noty({
                text: 'Unexpected Error!',
                layout: 'topCenter',
                timeout: 5000,
                closeWith: ['click', 'hover'],
                type: 'error'
                });
        }

    })
}




function update_reference_progress(status_url, status_div) {
    $("#progress_bar_2").fadeIn();
    // send GET request to status URL
    $.getJSON(status_url, function(data) {
        // update UI
        if(Number.isNaN(parseInt(data['current'], 10) * 100 / parseInt(data['total'], 10)) == true) {
            percent = 0;      
        } else {
            percent = Math.floor(parseInt(data['current'], 10) * 100 / parseInt(data['total'], 10));
        }
        $(status_div.childNodes[1]).text(percent + '%');
        $(status_div.childNodes[2]).text(data['message']);
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                // show result in earnings table
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
                table_.rows.add(data['result']).draw();
                $("tr").addClass("table-dark");
                $("#cboe_results").fadeIn();
            }

            else {
                // something unexpected happened
                $("#noty").noty({
                    text: data['state'],
                    layout: 'topCenter',
                    timeout: 5000,
                    closeWith: ['click', 'hover'],
                    type: 'error'
                    });
                $("#progress_bar_2").fadeOut();        
            }
        }
        else {
            // rerun in 2 seconds
            setTimeout(function() {
                update_reference_progress(status_url, status_div);
            }, 2000);
        }
    });
}