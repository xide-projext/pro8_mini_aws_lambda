// 오버레이 열기
function openOverlay() {
    document.getElementById('overlay').style.display = 'flex';
    document.querySelector('.close-btn').style.display = 'block';
}

// 오버레이 닫기
function closeOverlay() {
    document.getElementById('overlay').style.display = 'none';
    document.querySelector('.close-btn').style.display = 'none';
}

// 입력된 내용 처리
function getValues() {
    var table = document.getElementById("myTable");
    var rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    for (var i = 0; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName('td');
        var values = [];

        for (var j = 0; j < cells.length - 1; j++) {  // 마지막 열은 삭제 버튼이므로 제외
            values.push(cells[j].getElementsByTagName('input')[0].value);
        }

        console.log("행 " + (i + 1) + "의 값: " + values.join(", "));
    }
    console.log(values)
}

function addRow() {
    var table = document.getElementById("myTable").getElementsByTagName('tbody')[0];
    var newRow = table.insertRow(table.rows.length);

    for (var i = 0; i < 3; i++) {
        var cell = newRow.insertCell(i);
        var input = document.createElement("input");
        input.type = "text";
        cell.appendChild(input);
    }

    var deleteCell = newRow.insertCell(3);
    var deleteButton = document.createElement("button");
    deleteButton.className = "delete-btn";
    deleteButton.innerHTML = "삭제";
    deleteButton.onclick = function() {
        deleteRow(this);
    };
    deleteCell.appendChild(deleteButton);
}

function deleteRow(btn) {
    var row = btn.parentNode.parentNode;
    row.parentNode.removeChild(row);
}
