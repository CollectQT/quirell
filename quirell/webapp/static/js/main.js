$(document).ready(function(){


    // Image Upload Section
    $('.cloudinary-fileupload').bind('fileuploadstart', function(e, data) {
        $('progress').css("display", "inline-block")
    })
    $('.cloudinary-fileupload').bind('fileuploadprogress', function(e, data) {
        $('progress').attr("value", Math.round((data.loaded * 100) / data.total))
    })
    $('.cloudinary-fileupload').bind('fileuploadfail', function(e, data) {
        $('.upload_status').text(data)
    })
    $('.cloudinary-fileupload').bind('cloudinarydone', function(e, data) {
        $('.img_preview').attr("src", data.result.url)
        $('progress').css("display", "none")
        $('.upload_status').text('Upload Complete!')
        ajax_post($('#profile_edit_form'))
        // hide progress bar
    })


    // form AJAX section
    var ajax_post = function($form) {
        $.ajax({
            url: $form.attr("action"),
            data: $form.serialize(),
            type: $form.attr("method"),
        })
    }
    // do an AJAX post request if any of the profile edit fields besides
    // file inputs change
    $('#profile_edit_form input[type!="file"]').on("change", function() {
        ajax_post($('#profile_edit_form'))
    })
    // overide profile edit submission to use AJAX
    $('#profile_edit_form').on("submit", function(event) {
        ajax_post($(this))
        event.preventDefault()
    })


    // Angular JS
    angular
        .module('Quirell', [
        ])
        // local storage controller, ported from another project not currently functional
        .controller('formController', ['$scope', '$localStorage', function ($scope, $localStorage) {
            $scope.storage = $localStorage;
            $scope.formdata = {};

            // storage -> form
            for (var key in $scope.storage) {
                if (key[0] !== '$') {
                    $scope.formdata[key] = $scope.storage[key];
                    $('#form-delete').css('opacity', 1);
                }
            }

            // form -> storage
            $scope.processForm = function () {
                for (var key in $scope.formdata) {
                    if ($scope.userForm[key].$valid) {
                        $scope.storage[key] = $scope.formdata[key];
                        console.log('set', key, $scope.storage[key]);
                        $('#form-delete').css('opacity', 1);
                    }
                }
                if ($scope.userForm.$valid) {
                    $scope.changeView('/confirm');
                }
            };

            $scope.ClearStorage = function () {
                $('#form-delete').css('opacity', 0.1);
                for (var key in $scope.formdata) {
                    delete $scope.formdata[key];
                    delete $scope.storage[key];
                }
            };
        }])
})
