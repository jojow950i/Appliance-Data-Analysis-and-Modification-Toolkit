function window_resize() {

    //console.log("window: "+jQuery(window).width());
    //console.log("body: "+$("body").css("width"))

    var winWidth = parseInt($("body").css("width"), 10), availableAppliancesWidth, availableAppliancesPosition;
    //console.log(winWidth)

    var bodyHeight = jQuery(window).height() - jQuery("footer").outerHeight() - jQuery(".header").outerHeight();
    jQuery(".contentChoose").height(bodyHeight);
    jQuery(".contentChooseInner").height(bodyHeight-20);



    availableAppliancesWidth = Math.ceil((winWidth - 30 - jQuery("#DatSets").outerWidth()-jQuery("#mainSetup").outerWidth())/2.0);
    availableAppliancesPosition = jQuery("#DatSets").outerWidth()+10;

    var chosenAppliancesWidth = winWidth - jQuery("#DatSets").outerWidth() - availableAppliancesWidth - jQuery("#mainSetup").outerWidth() - 30;
    chosenAppliancesPosition = availableAppliancesPosition + availableAppliancesWidth +10;

    jQuery("#availableAppliancesMenu").width(availableAppliancesWidth );
    $("#availableAppliancesMenu").css('left', availableAppliancesPosition);

    jQuery("#chosenAppliancesMenu").width(chosenAppliancesWidth );
    $("#chosenAppliancesMenu").css('left', chosenAppliancesPosition);

    jQuery("#DatSets").height(bodyHeight);

    var availableAppliancesListHeight = jQuery("#availableAppliances").innerHeight() - jQuery("#availableAppliancesToolbar").outerHeight();
    jQuery("#availableAppliancesList").height(availableAppliancesListHeight - 20);

    chosenAppliancesListHeight = jQuery("#chosenAppliances").innerHeight() - jQuery("#chosenAppliancesToolbar").outerHeight();
    jQuery("#chosenAppliancesList").height(chosenAppliancesListHeight - 20);

    jQuery("#mainSetup").height(bodyHeight)
    $("#mainSetup").css('left', chosenAppliancesPosition+chosenAppliancesWidth+10);

    jQuery("#pageFooter").width(winWidth)
}
