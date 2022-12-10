let $MAIN_CONTAINER = $("#main-container");
let $FOOTER = $('.footer');
let $SUBFOOTER = $("#subfooter");

let $TEXT_SWITCH = $("#text-switch");
let $TEXT_HEADER_INPUT = $("#text-header");
let $TEXT_SUBHEADER_INPUT = $("#text-subheader");
let $TEXT_CLEAR_LINK = $("#text-clear");

let $BTN_DOWNLOAD = $("#download");

const WINDOW_WIDTH = $(window).width();
const WINDOW_HEIGHT = $(window).height();
const FRAME_MAX_WIDTH = WINDOW_WIDTH - 32;
const FRAME_MAX_HEIGHT = WINDOW_HEIGHT - 60 - 60 - 32;

let FRAME_WIDTH = null;
let FRAME_HEIGHT = null;
let FRAME_SCALE = null;
let FRAME_UPSCALE = null;
let OUTPUT_WIDTH = null;
let OUTPUT_HEIGHT = null;
let FRAME_NAME = null;
let FILE = null;

const rgb2hex = (rgb) => `${rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/).slice(1).map(n => parseInt(n, 10).toString(16).padStart(2, '0')).join('')}`

$(document).ready(function () {
    $SUBFOOTER.css('display', 'none');
    $FOOTER.hide();
});

function start(ratio_width, ratio_height, width, height, name) {
    OUTPUT_WIDTH = width;
    OUTPUT_HEIGHT = height;
    FRAME_NAME = name;
    $MAIN_CONTAINER.html('');

    FRAME_WIDTH = FRAME_MAX_WIDTH;
    let ratio_point = FRAME_WIDTH / ratio_width;
    FRAME_HEIGHT = ratio_point * ratio_height;

    if (FRAME_HEIGHT > FRAME_MAX_HEIGHT) {
        FRAME_HEIGHT = FRAME_MAX_HEIGHT;
        ratio_point = FRAME_HEIGHT / ratio_height;
        FRAME_WIDTH = ratio_point * ratio_width;
    }

    FRAME_SCALE = FRAME_WIDTH / OUTPUT_WIDTH;
    FRAME_UPSCALE = OUTPUT_WIDTH / FRAME_WIDTH;

    createContainer();
}

function createContainer() {
    let $frame_container = $($("template#default-frame").html());
    let $frame = $frame_container.find('#frame');
    let $image_upload_container = $($("template#image-upload-container").html());

    $frame_container
        .width(FRAME_WIDTH)
        .height(FRAME_HEIGHT)
        .css('transform', `scale(${FRAME_SCALE})`)
        .css('transform-origin', 'left top');
    $frame
        .width(OUTPUT_WIDTH)
        .height(OUTPUT_HEIGHT)
        .css('background-color', $('.color-choice.active').css('background-color'));
    $image_upload_container.prependTo($frame);
    $frame_container.appendTo($MAIN_CONTAINER);

    $FOOTER.show();

    let $file_upload_btn = $frame_container.find('.btn-add-image');
    let $file_upload_input = $frame_container.find('.file-select');

    $file_upload_btn.on('click', function () {
        $frame_container.find('.file-select').trigger('click');
    })

    $file_upload_input.on('change', function (event) {
        let img = document.createElement('img');
        $image_upload_container.remove();
        let img_width;
        let img_height;
        let objectUrl = URL.createObjectURL(event.target.files[0]);
        FILE = event.target.files[0];
        img.onload = function () {
            img_width = this.width;
            img_height = this.height;
            URL.revokeObjectURL(objectUrl);
        };
        img.src = objectUrl;
        let $img = $(img);
        let height = (img_width / img_height) * OUTPUT_WIDTH;
        $img.width(OUTPUT_WIDTH).height(height);
        $frame.prepend($img);
        $file_upload_input.val('');
    })

    let $sign = $frame.find('#sign');
    $sign.hide();
    $TEXT_HEADER_INPUT.on('input', function () {
        $frame.find('.sign-header').html($TEXT_HEADER_INPUT.val());
    })
    $TEXT_SUBHEADER_INPUT.on('input', function () {
        $frame.find('.sign-subheader').html($TEXT_SUBHEADER_INPUT.val());
    })
    $TEXT_CLEAR_LINK.on('click', function () {
        $TEXT_HEADER_INPUT.val('').trigger('input');
        $TEXT_SUBHEADER_INPUT.val('').trigger('input');
    })
    $TEXT_SWITCH.on('change', function () {
        if ($TEXT_SWITCH.is(':checked')) {
            $sign.css('transform', `scale(${FRAME_UPSCALE})`);
            $sign.show();
        } else {
            $sign.hide();
        }
    })

    $BTN_DOWNLOAD.on('click', function () {
        download();
        // const widthScale = OUTPUT_WIDTH / FRAME_WIDTH;
        // const heightScale = OUTPUT_HEIGHT / FRAME_HEIGHT;
        // let c = html2canvas(document.getElementById('frame'), {
        //     width: OUTPUT_WIDTH,
        //     height: OUTPUT_HEIGHT,
        //     backgroundColor: $frame.css('background-color'),
        // }).then(canvas => {
        //     let canvas_data = canvas.toDataURL('image/jpeg');
        //     let a = document.createElement('a');
        //     a.target = "_blank";
        //     a.href = canvas_data;
        //     a.click();
        // });
    })
}

function download() {
    let color_hex = rgb2hex($('.color-choice.active').css('background-color'));
    let formData = new FormData();
    formData.append("file", FILE, FILE.name);
    $.ajax({
        url: `/export/?width=${OUTPUT_WIDTH}&height=${OUTPUT_HEIGHT}&background=${color_hex}`,
        method: 'POST',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        xhrFields: {
            responseType: 'blob' // to avoid binary data being mangled on charset conversion
        },
        success: function (blob, status, xhr) {
            // let blob = new Blob([new Uint8Array(response, 0, response.length)], {type: 'image/jpeg'});
            // let blob = new Blob([response], {type: 'image/jpeg'});
            let urlCreator = window.URL || window.webkitURL;
            let href = urlCreator.createObjectURL(blob);
            let a = document.createElement('a');
            a.target = '_blank';
            a.href = href;
            a.download = 'parker-image-tools.jpeg';
            $("body").append(a);
            a.click();
            $("body").remove(a);
        },
        error: function (response) {
            console.error(response);
        },
    });
}

function scaleFrame($frame, up = false) {
    // TODO: один из вариантов скейлить пикчу перед сохранением, а не в css
}

function openMenu(selector) {
    if ($SUBFOOTER.find(selector).is(':visible')) {
        $SUBFOOTER.hide();
    } else {
        $SUBFOOTER.find('.container').children().not(selector).hide();
        $SUBFOOTER.find(selector).show();
        $SUBFOOTER.show()
    }
}

function colorChoice(event) {
    $('.color-choice').removeClass('active');
    let $colorButton = $(event.currentTarget);
    let color = $colorButton.css('background-color');
    $colorButton.addClass('active');
    $('#frame').css('background-color', color);
}