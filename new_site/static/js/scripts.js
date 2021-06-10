// функция обновления списка встречь
function update_meetings(user_id, csrftoken) {
    $.ajax({
        type: 'post',
        mode: 'same-origin',
        data: { "id": user_id, "csrfmiddlewaretoken": csrftoken },
        success: function (response) {
            $(".meetings").html("")
            $(".meetings").append("<h2>Встречи для согласования</h2>")

            if (!response.length) {
                $(".meetings").append('<p style="text-align:center;">Новых встречь нет.</p>')
            }

            //Для каждой встречи создать контейнер
            $.each(response, function (record) {
                rec = response[record];
                start_time = format_date(new Date(rec.start_time))
                end_time = format_date(new Date(rec.end_time))

                $(".meetings").append(`
                <div class="meeting" id="meeting_id_${rec.id}">
                <p><b>Организатор встречи:</b> ${rec.organizator_id__first_name} ${rec.organizator_id__last_name}</p>
                <p><b>Дата:</b> ${start_time.slice(0, 8)} <b>Время встречи с:</b> ${start_time.slice(-5)} <b>до</b>: ${end_time.slice(-5)}</>
                <p><b>Место:</b> ${rec.room_id__name}. <b>Тема:</b> ${rec.title}</p>
                <input type="submit" value="Принять" class="accept" onclick="send_meeting_answer('accept', String(this.parentNode.id))">
                <input type="submit" value="Отклонить" class="decline" onclick="send_meeting_answer('decline', String(this.parentNode.id))">
                </div>
                `)

            });

        },
    },
    )
};

/** функция добавления нулей к строкам. Принимает строку и количество символов 
 * для заполнения слева. Пример: zfill("5", 2) -> '05', zfill("2525", 2) -> '2525'*/
function zfill(num, length) {
    return String(num).padStart(length, "0");
};

// функция приведения даты к виду "02.05.2021 15:30"
function format_date(s_) {
    return `${zfill(s_.getDate(), 2)}.${zfill(s_.getMonth(), 2)}.${s_.getFullYear()} ${zfill(s_.getHours(), 2)}:${zfill(s_.getMinutes(), 2)}`
};


// функция вызывается при подтверждении/отклоненнии встречи менеджером и возвращает html-заглушку
// на месте встречи 
function create_html_answer(answer, container_id) {

    if (answer == "accept") {
        answer_local = "подтвердили"
        bgcolor = "rgb(224, 247, 212)"
    } else {
        answer_local = "отклонили"
        bgcolor = "rgb(247, 212, 212)"
    }

    $(`#${container_id}`).html(`
                <p style="background-color: ${bgcolor};">Вы ${answer_local} встречу!</p>
                `)

}

// формирует сообщение для уведомлений через каналы
function create_notification(e) {
    const data = JSON.parse(e.data)

    if (data.answer == "accept") {
        var answer = "подтвердил(а)"
    } else {
        var answer = "отклонил(а)"
    }

    title_str = `Собрание в ${format_date(new Date(data.start_time))}\nТема: ${data.title}`
    body_str = `${data.manager_id__first_name} ${data.manager_id__last_name} ${answer} встречу`

    return { "title": title_str, 'body': body_str }
}

// функция относится к созданию встречи
// меняет значение даты конца, если начальная дата изменилась и стала меньше конечной 
function start_time_changed(event) {

    var start_time = new Date(document.getElementById("id_start_time").value);
    var end_time = new Date(document.getElementById("id_end_time").value)

    if (end_time <= start_time) {
        var new_end_time = _add_and_format_time_for_datetime_local(start_time, 1);
        document.getElementById("id_end_time").value = new_end_time
    }
}

// функция относится к созданию встречи
// меняет значение даты начала, если конечная дата изменилась и стала меньше начальной
function end_time_changed(event) {
    var start_time = new Date(document.getElementById("id_start_time").value);
    var end_time = new Date(document.getElementById("id_end_time").value)

    //console.log(start_time, end_time)

    if (end_time <= start_time) {
        var new_start_time = _add_and_format_time_for_datetime_local(end_time, -1);
        document.getElementById("id_start_time").value = new_start_time


    }
}

// возвращает дату в текстовом формате, подходящую для вставки в datetime-local
function _add_and_format_time_for_datetime_local(s_, o_) {
    return `${s_.getFullYear()}-${zfill(s_.getMonth() + 1, 2)}-${zfill(s_.getDate(), 2)}T${zfill(s_.getHours() + o_, 2)}:00`

};

// возвращает информацию о комнате add_room
function get_room_info(event) {

    var del_button = document.getElementById("decline")
    var is_del_exists = document.body.contains(del_button)

    var id = document.getElementById('id_id');
    var room = document.getElementById('id_name');
    var seats = document.getElementById('id_seats');
    var board = document.getElementById('id_board');
    var projector = document.getElementById('id_projector');
    var description = document.getElementById('id_description');

    if (id.value != 0) {
        document.getElementById('accept').innerText = "Обновить"
        if (!is_del_exists) {

            $("#del_container").append(`<button name="delete" class="decline" id="decline" 
                onclick="delete_room()">Удалить</button>`)
        }
        $.ajax({
            type: 'post',
            headers: { "X-Requested-With": "XMLHttpRequest" },
            data: { "id": id.value, "csrfmiddlewaretoken": csrftoken },
            success: function (response) {
                room.value = response.name
                seats.value = response.seats
                board.checked = response.board
                projector.checked = response.projector
                description.value = response.description
                console.log(response);


            },
            error: { "response": "Запись не найдена!" }
        }
        )
    } else {
        document.getElementById('accept').innerText = "Создать"
        room.value = ''
        seats.value = 1
        board.checked = false
        projector.checked = false
        description.value = ''
        if (is_del_exists) {
            $("#decline").remove()
        }
    }
}

//удаляет выбранную комнату в add_room
function delete_room() {

    var id = document.getElementById('id_id');

    if (id.value != 0) {
        $.ajax({
            type: 'POST',
            data: { 'id': id.value, "csrfmiddlewaretoken": csrftoken },
            success: function (response) {
                window.location.replace("/")
            },
            error: function () {
                alert("что-то пошло не так!");
            }
        })
    }
}