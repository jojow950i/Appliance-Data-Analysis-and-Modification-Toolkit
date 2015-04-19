function sendGenerateOrder(){

    $("#progress").val('0')
    document.getElementById("generateButton").disabled = true
    console.log("generate disabled: " +document.getElementById("generateButton").disabled)
    console.log("download disabled: " +document.getElementById("downloadButton").disabled)


    appliances = '{\"appliances\":{'

    length = applianceList_chosen.items.length;
    c_length = 0;
    applianceList_chosen.items.forEach(function (current_appliance) {
        name = current_appliance._values.name_chosen;


        sizes = ["Small", "Medium", "Large"];

        size = "";

        id=current_appliance._values.id_chosen;

        resampling = document.getElementById('resampling'+id).value
        median = document.getElementById('median'+id).value
        fill = document.getElementById('fillMissing'+id).value

        console.log(median)


        sizes.forEach(function (entry) {
            current = entry + "button" + id;
            if (document.getElementById(current).checked) {
                size = entry;
            }
        });

        c_datasets = current_appliance._values.datasets_list;
        entry = '{'+
            '\"name\":\"'+ name+'\",'+
            '\"size\":\"' +size+'\",'+
            '\"datasets\":'+ c_datasets+','+
            '\"resampling\":\"'+ resampling+'\",'+
            '\"median\":\"'+ median+'\",'+
            '\"fill\":\"'+ fill+'\"'+
            '}';
        appliances+='\"'+id+'\":'+entry;
        if(length != c_length+1){
            appliances+=','
        }
        c_length++;

        //console.log(current_appliance)
    });

    appliances+='}}';

    //console.log(appliances)

    timeframe = '';

    if(document.getElementById('oneHour').checked){
        timeframe = "1H";
    }else if(document.getElementById('oneDay').checked){
        timeframe = "1D";
    }else if(document.getElementById('oneWeek').checked){
        timeframe = "1W";
    }else if(document.getElementById('otherTime').checked) {
        timeframe = document.getElementById('setTimeInterval').value;
    }

    id = document.getElementById("downloadForm").getAttribute("name")

    noise = 0;
    if(document.getElementById('genNoise').checked){
        noise = document.getElementById('noiseLevel').value;
    }

    missing = 0
    if(document.getElementById('genMissing').checked){
        missing = document.getElementById('missingLevel').value;
    }

    calcTotalComplexity = document.getElementById('calcTotalComplexity').checked


    message = {
        'appliances': appliances,
        'timeframe' : timeframe,
        'id': id,
        'noise' : noise,
        'missing' : missing,
        'calcTotalComplexity' : calcTotalComplexity
    };

    $.postJSON("/generate", message,null);

    console.log("finished ")

    //document.getElementById("downloadButton").disabled = false;
    //document.getElementById("generateButton").disabled = false;



}

var status_updater = {
    errorSleepTime: 500,


    poll: function() {
        id = document.getElementById("downloadForm").getAttribute("name")
        args = {'id':id}
        $.ajax({url: "/update", type: "POST", dataType: "text",
                data: $.param(args), success: status_updater.onSuccess,
                error: status_updater.onError});

    },

    onSuccess: function(response) {
        try {
            status_updater.newMessages(eval("(" + response + ")"));
        } catch (e) {
            status_updater.onError();
            return;
        }

        status_updater.poll()
        //status_updater.errorSleepTime = 500;
        //window.setTimeout(status_updater.poll, 0);
    },

    onError: function(response) {
        status_updater.errorSleepTime *= 2;
        console.log("Poll error; sleeping for", status_updater.errorSleepTime, "ms");
        //window.setTimeout(status_updater.poll, status_updater.errorSleepTime);
    },

    newMessages: function (response) {

        if('%' == response.update[0]){
            vars = response.update.split(' ')
            $("#progress").val(vars[1])
        }
        else if('<finished>' == response.update){
            console.log("fffff")
            document.getElementById("downloadButton").disabled = false;
            document.getElementById("generateButton").disabled = false;
            console.log("generate disabled: " +document.getElementById("generateButton").disabled)
            console.log("download disabled: " +document.getElementById("downloadButton").disabled)
        }
        else{
            $("#outputStatus").append(response.update);
            $("#statusArea").animate({ scrollTop: $("#statusArea")[0].scrollHeight }, "slow");
            //console.log($("#statusArea")[0].scrollHeight )
        }


    }
}