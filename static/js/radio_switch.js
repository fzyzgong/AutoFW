$(function(){
	showCont();
	$("input[name=case_type]").click(function(){
		showCont();
	});
});

function showCont(){
	switch($("input[name=case_type]:checked").attr("value")){
		case "module_type":
			$("#list_case").hide();
			$("#module_case").show();
			break;
		case "list_type":
			$("#module_case").hide();
			$("#list_case").show();
			break;
		default:
			break;
	}
}