/**
 * Created by johannesholzl on 18.12.14.
 */
var i = 1;
var checked_datasets = {};
var userList, options;

$(function () {

    window_resize();

    jQuery(window).resize(function () {
        window_resize();
        //console.log("resize")
    });


    options = {
        valueNames: ['name', 'switchableButtons', 'modifyButton'],
        item: '<li class="entryChosen"><table style=\"width:100%\">' +
        '<tr>' +
        '<td><h4 style="width: 150px" class="name"></h4></td>' +
        '<td style="margin-right: 0; margin-left: auto"><div class="switchableButtons"></div></td>' +
        '<td><div class="modifyButton"></div></td>' +
        '</tr></table></li>'
    };

    userList = new List('availableAppliances', options);

    options_chosen = {
        valueNames: ['name_chosen', 'switchableButtons_chosen', 'modifyButton_chosen', 'editButton_chosen','id_chosen', 'datasets', 'datasets_list'],
        item: '<li><table style=\"width:100%\">' +
        '<tr>' +
        '<td class="id"></td>'+
        '<td style=\"width: 200px\"><h3 class="name_chosen"></h3></td>' +
        '<td><div class="switchableButtons_chosen"></div></td>' +
        '<td style=\"text-align: right\"><div class="editButton_chosen" style=\"text-align: right\"></div></td>' +
        '<td style=\"text-align: right\"><div class="modifyButton_chosen" style=\"text-align: right\"></div></td>' +
        '</tr>' +
        '<tr>' +
        '<td></td><td><div class="datasets"></div>' +

        '</td><td></td><td></td>' +
        '</tr>' +
        '</table></li>'
    };

    applianceList_chosen = new List('chosenAppliances', options_chosen);

    userList.search('', ['name'])
    applianceList_chosen.search('', ['name_chosen'])

});

$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};


    console.log("start");
    getCheckboxes();

    status_updater.poll()
});

function getEntries() {

    //console.log(checked_datasets)
    var message = {"datasets": (1, 2)}
    $.postJSON("/entry/all", checked_datasets,
        function (response) {
            var va = $(response.v);


            for (var v = 0; v < va.length; v++) {
                $("#entries").append(va[v].html);
            }
        }
    );
}

function getCheckboxes() {
    $.postJSON("/checkboxes/all", "123",
        function (response) {
            //$("#entries").append($(response.html));

            var va = $(response.v);


            for (var v = 0; v < va.length; v++) {
                $("#DatSets").append(va[v].html);
            }
        }
    );
}

jQuery.postJSON = function (url, args, callback) {
    $.ajax({
        url: url, data: $.param(args), dataType: "text", type: "POST",
        success: function (response) {
            if (callback) callback(eval('(' + response + ')'));
        }, error: function (response) {
            console.log("ERROR:", response);
        }
    });
};


function correctPosition(button){
    console.log("hover")

    yTrans = document.getElementById('chosenAppliancesList').scrollTop
    yPosButton = getOffset(document.getElementById(button.id)).top
    yPos = yPosButton - yTrans -20
    menuHeight = jQuery("#"+button.querySelector('.menuDropdown').id).outerHeight()

    yPosContainer = getOffset(document.getElementById('chosenAppliances')).top
    yPosLowerContainer = jQuery('#chosenAppliancesList').innerHeight() + yPosContainer

    console.log('mh:'+(menuHeight+yPos));
    console.log('lower: '+yPosLowerContainer);
    if(yPos + menuHeight > yPosLowerContainer){
        yPos = yPosLowerContainer - menuHeight;
    }

    button.querySelector('.menuDropdown').style.top = yPos

    console.log(yPosLowerContainer)

    console.log("top:"+button.querySelector('.menuDropdown').style.top)

}

function getOffset( el ) {
    var _x = 0;
    var _y = 0;
    while( el && !isNaN( el.offsetLeft ) && !isNaN( el.offsetTop ) ) {
        _x += el.offsetLeft - el.scrollLeft;
        _y += el.offsetTop - el.scrollTop;
        el = el.offsetParent;
    }
    return { top: _y, left: _x };
}

function removeChosen(id) {
    applianceList_chosen.remove('id_chosen', id);
}


