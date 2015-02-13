$(document).ready(function(){
    // Image Upload Section
    var status_elem = $('.upload_status')
    var url_elem = $('.avatar_url')
    // whenever a picture is set for uploading, load it into preview box(es)
    $('.img_upload').change(function(){
        $('.img_preview').attr('src', window.URL.createObjectURL(this.files[0]))
    })
    // function bind for profile picture uploads
    $('.img_upload.profile_picture').change(function() {
        s3_upload(is_profile_picture=true, input_object=this, status_elem, url_elem)
    })
    // function bind for any other sort of picture
    $('.img_upload.normal_picture').change(function() {
        s3_upload(is_profile_picture=false, input_object=this, status_elem, url_elem)
    })
})

function s3_upload(is_profile_picture, input_object, status_elem, url_elem){
    var s3upload = new S3Upload({
        input_object: input_object,
        is_profile_picture: is_profile_picture,
        onProgress: function(percent, message) {
            status_elem.html('Upload progress: ' + percent + '% ' + message)
        },
        onFinishS3Put: function(url) {
            status_elem.html('Upload completed. Uploaded to: '+ url)
            url_elem.val(url)
        },
        onError: function(status) {
            status_elem.html('Upload error: ' + status)
        }
    })
}
