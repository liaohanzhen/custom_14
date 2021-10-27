var _t = null;
var translations;
var current_lang
odoo.define('quick_order.quick_order', function (require) {
'use strict';
    var rpc = require('web.rpc');
    const core = require('web.core');
    const { qweb } = require('web.core');
    _t = core._t;

$(document).ready(function(){
    rpc.query({
        route: '/quick/get_translations',
        }).then(function (data) {
            translations = data[0];
            current_lang = data[1]['lang']
            var main_div = $('#main_div')
            var markup = '<h5><div class="row mt-2 mb-2"><div class="col-md-3">'+trans('Product Reference')+'</div>' +
            '<div class="col-md-1">'+trans('Qty')+'</div><div class="col-md-4">'+trans('Product')+'</div>' +
            '<div class="col-md-2">'+trans('Price')+'</div><div class="col-md-2">'+trans('Sum')+
            '</div></div></h5><div style="border-bottom: 1px solid black;">';
            main_div.append(markup);

            var num_of_lines = 8;
            for (var i=1; i <= num_of_lines; i++) {
                markup = '<div class="row my-2" id="row_no_' + i + '">';
                var storage_values = load_from_storage(i);
                if (storage_values != ""){
                    markup +=storage_values.html_values;
                    num_of_lines++;
                    }
                else {
                    markup +=add_new_row(i);
                    }

                markup +='</div><div style="border-bottom: 1px solid black;">';
                main_div.append(markup);
                if (storage_values != ""){
                    populate_from_storage(i,storage_values.values)
                    }

                $("#main_div").bind("change", "#quantity_input_"+i, function(el){
                    update_prices(el);
                    });
                }

            markup = "<div class='row my-2'><div class='col-md-auto pr-0'><a role='button' class='form-control btn btn-primary btn-danger w-auto te_theme_button' id=remove_all href='#'><span>"+trans('Empty whole order form')+"</span></a></div>" +
            "<div class='col-md-auto'><a role='button' class='form-control btn btn-primary w-auto check_btn te_theme_button' value='all' href='#'><span>"+trans('Check All')+"</span></a></div>" +
            "<div class='col-md-auto ml-auto'><a role='button' class='form-control btn btn-primary w-auto float-right cart_btn te_theme_button' href='#'><span>"+trans('Add To Cart')+"</span></a></div>" +
            "<input class='form-control cart_products' name='cart_products' hidden='true'></div></div>";
            main_div.append(markup);
            });

    function trans(word){
        var to_return = word;
        $.each(translations, function(index, value){
            if(value['src'] == word){
                to_return = value['value'];
                return false;
                }
            });
        return to_return;
        }

    function add_new_row (i){
        var markup = '<div class="col-md-3 pr-0" id="dropdown_input_' + i + '"><input type="search" class="search-product form-control" ' +
        'autocomplete="off" id=reference_input_' + i + '></div>' +
        '<div class="col-md-1 remove_qty_arrows"><input class="form-control quantity_input" id=quantity_input_' + i + ' type="number" min="0" style="width: 4.7vw;"></div>' +
        '<div class="col-md-4 d-flex"><button type="button" style="display:none !important;" class="form-control btn-primary w-auto check_btn te_theme_button" value=' + i +
        ' id=check_input_' + i +'>'+trans('Check')+'</button><select class="form-control w-auto d-none var_change"id="variant_select_' + i +
        '" name="variants"><option disabled selected value></option></select><input hidden id=product_pro_id_' + i + '></input>' +
        '<input hidden id=product_temp_id_' + i + '></input><a class="d-none" id=image_input_' + i +
        ' style="width: 80px;min-width: 80px;"></a><div class="ml-2" id=product_input_' + i +'></div></div>' +
        '<div class="col-md-2"><p id=price_input_' + i +'></p><input hidden id=tax_price_' + i + '></input><input hidden id=untax_price_' + i + '></input></div>' +
        '<div class="col-md-1"><input hidden id=currency_symbol_' + i + '></input><p style="text-align: center;" id=sum_input_' + i +'></p></div>' +
        '<div class="col-md-1 pl-0 text-right"><button class="form-control btn-primary btn-danger w-auto te_theme_button remove_product"  value=' + i + ' id=remove_input_' + i + '>X</button></div>';
        return markup;
        }

   $("#main_div").on("click", ".check_btn", function(){
       $(".product_dropdown").remove();
        var refs = [];
        if ($(this)[0].getAttribute('value') == 'all') {
            $("#main_div :input[id*='reference_input_']:not(:disabled)").each(function() {
                if ($(this).val()){
                    var obj = {}
                    var id = $(this)[0].id.replace("reference_input_","");
                    obj[id] = $(this).val();
                    refs.push(obj)
                }
            });
        } else {
            var id = $(this).val();
            var ref = $('#reference_input_' + id);
            if (ref.val()) {
                $('#reference_input_' + id).removeClass("border-danger");
                var obj = {}
                obj[id] = ref.val();
                refs.push(obj)
            } else{
                $('#reference_input_' + id).addClass("border-danger");
            }
        }
        if (refs.length > 0){
            rpc.query({
                route: '/quick/get_products_variants',
                params: {
                    params: refs,
                    }
            }).then(function (data) {
                for (var i=0; i < data.length; i++) {
                    $('#reference_input_' + data[i]['row']).prop("disabled", true );
                    $('#check_input_' + data[i]['row']).prop("disabled", true );
                    $('#check_input_' + data[i]['row']).hide();
                    if (data[i]['pro_id'] != false) {
                        $('#quantity_input_' + data[i]['row']).val(1);
                        $('#product_temp_id_' + data[i]['row']).val(data[i]['pro_id']);
                        if (data[i]['variants'].length > 0){
                            for (var j=0; j < data[i]['variants'].length; j++) {
                                var key = Object.keys(data[i]['variants'][j]);
                                var value = Object.values(data[i]['variants'][j])
                                $('#variant_select_' + data[i]['row']).append(new Option(value[0], key[0]));
                            }
                            $('#variant_select_' + data[i]['row']).addClass('d-inline');
                            $('#product_input_' + data[i]['row']).html(data[i]['pro_name'] + '<br><small>'+trans('There are different variants available.<br>Please select one.')+'</small>');
                        } else {
                            refs = [{'row_id': data[i]['row'], 'pro_id':data[i]['pro_id']}]
                            rpc.query({
                                route: '/quick/get_product_details',
                                params: {
                                    params: refs,
                                    }
                            }).then(function (data) {
                                if (data) {
                                    fill_data(data);
                                }
                            });
                        }
                    } else {
                        $('#quantity_input_' + data[i]['row']).prop("disabled", true );
                        $('#product_input_' + data[i]['row']).text(trans("Product Not Found")).addClass('text-danger');
                    }
                }
            });
        }
        return false;
  });

    $("#main_div").on("change", ".var_change", function(){
        var refs = [];
        var obj = {}
        obj['row_id'] = $(this)[0].id.replace("variant_select_","");
        obj['att_val'] = this.value
        obj['pro_id'] = $('#product_temp_id_' + obj['row_id']).val();
        refs.push(obj)
        // Duplication Check
        $("#main_div :input[id*='variant_select_']:disabled").each(function() {
            let id = $(this)[0].id.replace("variant_select_","");
            let pro_id  = $('#product_temp_id_' + id).val();
            if (refs[0]['pro_id'] == $('#product_temp_id_' + id).val() && refs[0]['att_val'] == this.value) {
                alert(trans('This Product already selected with the same Variant'));
                refs = [];
                return false;
            }
        });
        if (refs.length > 0){
            rpc.query({
                route: '/quick/get_product_details',
                params: {
                    params: refs,
                    }
            }).then(function (data) {
                fill_data(data);
            });
        }
        return false;
    });

    function fill_data(data) {
        for (var i=0; i < data.length; i++) {
            $('#variant_select_' + data[i]['row']).prop("disabled", true );
            $('#variant_select_' + data[i]['row']).addClass('d-none').removeClass('d-inline');
            $('#image_input_' + data[i]['row']).html('<img style="max-width: 100%" src="/web/image/product.product/' +
            data[i]['pro_id'] + '/image_1024">').attr('href', '/shop/' + $('#product_temp_id_' + data[i]['row']).val() +
            '#attr=' + data[i]['attributes']).addClass('d-inline').removeClass('d-none');
            var product_description = "";
            if (data[i]['pro_desc'] != ""){
                product_description = '<br><div class="tooltip"><span class="tooltiptext">' + data[i]['pro_desc'] +
                 '</span>' + data[i]['pro_desc'].slice(0, 100) + ' ...</div><small>'+trans('Delivery time approx.')+' '
                 + data[i]['delivery'] + '-' + (data[i]['delivery'] + 1) + ' ' +trans('working days')+'</small>';
            } else {
                product_description = '<br><small>'+trans('Delivery time approx.')+' ' + data[i]['delivery'] + '-' + (data[i]['delivery'] + 1) + ' '+trans('working days')+'</small>';
            }

            $('#product_input_' + data[i]['row']).html(data[i]['pro_name'] + product_description);
            $('#product_pro_id_' + data[i]['row']).val(data[i]['pro_id']);
            $('#price_input_' + data[i]['row']).html(data[i]['currency_symbol'] + "" + get_formatted_num(Number.parseFloat(data[i]['tax_price']).toFixed(2)));
            $('#tax_price_' + data[i]['row']).val(data[i]['tax_price']);
            $('#untax_price_' + data[i]['row']).val(data[i]['untax_price']);
            $('#currency_symbol_' + data[i]['row']).val(data[i]['currency_symbol']);
            $('#sum_input_' + data[i]['row']).text(data[i]['currency_symbol'] + "" + get_formatted_num((Number.parseFloat(data[i]['tax_price']).toFixed(2)*$('#quantity_input_' + + data[i]['row']).val())));

            remove_from_storage(data[i]['row']);
            add_to_storage(data[i]['row']);
        }
        return true
    }

    $("#main_div").on("click", ".cart_btn", function(){
        var products = [];
        $("#main_div :input[id*='variant_select_']:disabled").each(function() {
            var obj = {}
            var id = $(this)[0].id.replace("variant_select_","");
            obj['pro_id'] = $('#product_pro_id_' + id).val();
            obj['qty'] = $('#quantity_input_' + id).val();
            products.push(obj);
        });
        if (products.length > 0){
            $('.cart_products').val(JSON.stringify(products));
            $('#quick_order_form').submit();
            remove_from_storage("all");
        } else {
            alert(trans('Items not ready for cart'));
        }
        return false;
      });

    $("#main_div").on("click", ".remove_product", function(el){
        var row_number = $("#"+el.target.id).val();
        remove_from_storage(row_number);
        reset_values(row_number)
        return false;
    });

    $("#main_div").on("click", "#remove_all", function(el){
        remove_from_storage("all");
        location.reload();
        return false;
    });

//Call function on Key press for product Dropdown
  $("#main_div").on("keyup", ".search-product", function(){
    var id = $(this)[0].id.replace("reference_input_","");
    rpc.query({
        route: '/shop/products/autocomplete',
        params: {'term': $(this).val()},
    }).then(function (data) {
        var input = $('#dropdown_input_' + id);
        input.find('.dropdown-menu').remove();
        input.addClass('dropdown show');
        input.displayPrice = input.displayImage = true
        if (data) {
            var products = data['products'];
            var menu = $(qweb.render('website_sale.productsSearchBar.autocomplete', {
                products: products,
                widget: input,
            }));
            menu.addClass('product_dropdown');
            menu.css({'min-width': 520, 'margin-left': 15});
            menu.find('h6').css({'max-width': '250px', 'text-overflow': 'ellipsis', 'overflow': 'hidden'});
            menu.find('.flex-shrink-0').css({'max-width': '150px', 'text-overflow': 'ellipsis', 'overflow': 'hidden'});
            menu.find('a').each(function() {
                $(this).attr("href", "javascript:void(0)");
                var ref = ''
                var thisInput = $(this)
                var pro_temp_id = $(this).find('img').attr('src').match("product.template/(.*)/")[1];
                rpc.query({
                    route: '/quick/get_product_reference',
                    params: { params : pro_temp_id},
                }).then(function (data) {
                    if (data) {
                        ref = data
                        thisInput.find('h6').after('<p>' + data + '</p>');
                    }
                });
                thisInput.click(function() {
                    thisInput.parent().siblings().val(ref);
                    $("#check_input_"+id).trigger("click");
                });
            });
            input.append(menu);
        }
    });
    return false;
  });

  function get_storage_elements(){
        return ['reference_input','quantity_input','variant_select','product_temp_id','product_pro_id','tax_price','untax_price','currency_symbol'];
  }

  function update_prices(element){
        var row_number = element.target.id.replace("quantity_input_","");
        var price = $('#tax_price_' + row_number).val();
        var qty = $('#quantity_input_' + row_number).val();
        var currency_symbol = $('#currency_symbol_' + row_number).val();
        var formated_value = Number.parseFloat(price * qty).toFixed(2);
        $('#sum_input_' + row_number).text(currency_symbol + "" + get_formatted_num(formated_value));
        remove_from_storage(row_number);
        add_to_storage(row_number);
  }

   function add_to_storage(row_number){
        var storage_array = [];
        var populated_array = [];
        if (typeof(Storage) !== "undefined" && typeof(localStorage) !== "undefined") {
                if (typeof(localStorage.quick_order_details) !== "undefined" && localStorage.quick_order_details != ''){
                    storage_array = JSON.parse(localStorage.quick_order_details);
                }

                populated_array = populate_storage_elements(row_number);
                var temp_object = {row_id:row_number,html_values:$("#row_no_"+row_number).html(),values:populated_array};
                storage_array.push(temp_object);
                localStorage.setItem("quick_order_details", JSON.stringify(storage_array));
        }
  }

  function populate_storage_elements(row_number){

        var return_array = [];
        var elements_array = get_storage_elements();
        for(var index=0;index < elements_array.length;index++){
            var current_element = elements_array[index]+"_"+row_number;
            if (document.getElementById(current_element)){
                var temp_object = {name:elements_array[index],value:document.getElementById(current_element).value};
                return_array.push(temp_object);
            }
        }
        return return_array;
  }

    function load_from_storage(row){
        var return_value = "";
        if (typeof(Storage) !== "undefined" && typeof(localStorage) !== "undefined") {
                if (typeof(localStorage.quick_order_details) !== "undefined" && localStorage.quick_order_details != ''){
                    var stored_array = JSON.parse(localStorage.quick_order_details);
                    for (var row_index in stored_array) {
                        var current_row = stored_array[row_index].row_id;
                        if (row == current_row){
                             return_value = stored_array[row_index];
                        }
                    }
                }
        }
        return return_value;
  }

  function populate_from_storage(current_row,stored_values){

        for (var index=0;index < stored_values.length;index++){
            var current_row_element = stored_values[index].name +"_"+current_row;
            if (document.getElementById(current_row_element)){
                if (stored_values[index].name == "variant_input"){
                    $('#' + current_row_element).text($('#' + current_row_element + ' option:selected').text());
                } else {
                    document.getElementById(current_row_element).value=stored_values[index].value;
                }
            }
        }
  }

  function remove_from_storage(delete_row){

        if (typeof(Storage) !== "undefined" && typeof(localStorage) !== "undefined" && typeof(localStorage.quick_order_details) !== "undefined") {
                if (delete_row == "all"){
                    localStorage.setItem("quick_order_details", "");
                } else if (localStorage.quick_order_details != ''){
                    var stored_array = JSON.parse(localStorage.quick_order_details);
                    var updated_storage_array = [];
                    var updated_element_array = [];
                    for (var row_index in stored_array) {
                        var stored_html_values = stored_array[row_index].html_values;
                        var stored_values = stored_array[row_index].values;
                        var current_row = stored_array[row_index].row_id;
                        if (current_row == delete_row){
                            continue;
                        }
                        for (var index=0;index < stored_values.length;index++){
                            var temp_object = {name:stored_values[index].name,value:stored_values[index].value};
                            updated_element_array.push(temp_object);
                        }
                        var temp_object = {row_id:current_row,html_values:stored_html_values,values:stored_values};
                        updated_storage_array.push(temp_object);
                    }
                    localStorage.setItem("quick_order_details", JSON.stringify(updated_storage_array));
                }
        }
  }

  function reset_values(row){
       var row_html = add_new_row(row);
        $("#row_no_"+row).html("");
        $("#row_no_"+row).html(row_html);
  }

  $(document).ready(function() {
    $(window).keydown(function(event){
        if(event.keyCode == 13) {
        event.preventDefault();
        return false;
        }
    });
  });

 $(document).click(function(){
    if (document.getElementsByClassName("dropdown-menu show")){
        $(".dropdown-menu.show").remove();
    }
 });

    function get_formatted_num(num) {
        if (current_lang) {
            let languageFormat = Intl.NumberFormat(current_lang.replace('_', '-'));
            return languageFormat.format(num);
        } else return num
    }
});
});
