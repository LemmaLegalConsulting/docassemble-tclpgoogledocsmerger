from docassemble.base.util import CustomDataType, DAValidationError, word

class BetterMultiselect(CustomDataType):
  name = 'ourmultiselect'
  container_class = 'tclp-multiselect-container'
  input_class = 'tclp-multiselect multiselect damultiselect'
  javascript="""\
$(document).ready(function() {
  $(".tclp-multiselect").attr("multiple", "");
  $(".tclp-multiselect").each(function(){
    var origElem = this;
    $(origElem).hide();
    $(origElem).attr('type', 'hidden');
    //var selectElem = $('<select multiple="" class="tclp-multiselect damultiselect></select>');
    var selectElem = document.createElement("p");
    selectElem.innerHTML = "Text.";
    //var data = $(origElem).attr("data-code-options");
    //for (var i = 0; i < data.length; i++) {
    //  var selectOption = $('<option value="a">' + data[i] + '</option>');
    //  $(selectElem).append(selectOption);
    //}
    $(origElem).before(selectElem);
    
  });
  
  //$(".tclp-multiselect").multiselect({
  //    enableCaseInsensitiveFiltering: true,
  //    inheritClass: true,
  //    enableClickableOptGroups: true
  //});
});
"""
  code_parameters = ["code_options"]
  input_type="multiselect"
  
  @classmethod
  def validate(cls, item):
    return True
  
  @classmethod
  def transform(cls, item):
    returnValue = []
    log(f"The choices!: {item}")
    return returnValue
  
  