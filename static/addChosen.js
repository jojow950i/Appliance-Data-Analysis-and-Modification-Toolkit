
function addChosen(from, buttons, name, small, medium, large) {

    buttons += i;
    var id = from + i;

    i++;

    app_name = name;

    var all = "<div class='tmp_id' id=\"" + id + "\">";

    chosen = false;

    var items = ["Small", "Medium", "Large"];
    var itemVals = {"Small":small, "Medium":medium, "Large":large};
    items.forEach(function (entry) {
        currentRadio = 'rdo'+entry+'' + from
        var t_id = entry + "" + buttons;
        all += "<input ";
        if (document.getElementById(currentRadio).checked) {
            chosen = true
            all += "checked "
            $('rdo'+entry+'' + from).attr('checked', false);
        }
        if (document.getElementById(currentRadio).disabled){
            all+= "disabled=\"true\" "
        }

        amount = itemVals[entry];

        all += "class=\"selectable\" type=\"radio\" id=\"" + t_id + "\" name=\"" + buttons + "\"  onclick=\"\"/>" +
        "<label style=\"font-size:10px;\" class=\"selectableLabel\" for=\"" + t_id + "\">" + entry +" ("+amount+")</label>"


    });

    if(!chosen){
        alert("Please select size of appliance!")
        return
    }

    all += "</div>";

    var buttonRemove = "<input style=\"font-size:10px;float:right\" type=\"button\" style=\"font-size:12px;\" class=\"ButtonRemove\" value=\"Remove\" onclick=\"removeChosen(" + id + ")\"/>";

    var buttonEdit = '<div class="ButtonEdit" id="edit'+id+'" onmouseover="correctPosition(this)">Edit'//"<input style=\"font-size:10px;float:right\" type=\"button\" style=\"font-size:12px;\" class=\"ButtonEdit\" value=\"Edit\" onclick=\"removeChosen(" + id + ")\"/>";

    buttonEdit += '</br><div class="menuDropdown" id="dropdown'+id+'"><table>'

    buttonEdit += '<tr></tr><td>Resampling Rule:</td><td><input type="text" value="1S" id="resampling' + id + '"></td></tr>'
    buttonEdit += '<tr></tr><td>Fill Missing:</td><td><select style="width = 100%" id="fillMissing' + id + '">' +
    ' <option value="ffill">ffill</option>' +
    ' <option value="None">None</option>' +
    '</select></td></tr>'
    buttonEdit += '<tr></tr><td>Median Filter:</td><td><input type="text" id="median' + id + '"></td></tr>'
    buttonEdit += '</br>'

    buttonEdit += '</table></div></div>'

    datasets = new Array();

    var inc = 0;

    for (var key in
        checked_datasets
        ) {
        if (checked_datasets[key]) {
            datasets[inc] = key;
            inc++;
        }
    }

    show = "";

    for (var data = 0; data < datasets.length; data++) {
        show += datasets[data];
        if (datasets.length - 1 != data) {
            show += ", ";
        }
    }

    show="<div style='font-size: smaller'>"+show+"</div>";

    applianceList_chosen.add({
        name_chosen: app_name,
        switchableButtons_chosen: all,
        modifyButton_chosen: buttonRemove,
        editButton_chosen: buttonEdit,
        id_chosen: id,
        datasets: show,
        datasets_list: JSON.stringify(checked_datasets)
    });

    $("#" + id).buttonset();

    obj = document.getElementById("innerChosenAppliancesList");
    obj.scrollTop = obj.scrollHeight;
}