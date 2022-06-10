var config = {
    type: Phaser.WEBGL,
    width: 600,
    height: 750,
    scene: {
        preload: preload,
        create: create,
        update: update,
    }
};

var game = new Phaser.Game(config);
var figures = [[]];
figures.length = 0;
var pointers = [];
pointers.length = 0;
team = ''
var drag_start = {x:"",y:""};

function chess_to_pixel(chess) {
    if        (chess.x == 'A') {
        x = '75';
    } else if (chess.x == 'B') {
        x = '225';
    } else if (chess.x == 'C') {
        x = '375';
    } else {
        x = '525';
    };

    if        (chess.y == '1') {
        y = '675';
    } else if (chess.y == '2') {
        y = '525';
    } else if (chess.y == '3') {
        y = '375';
    } else if (chess.y == '4') {
        y = '225';
    } else {
        y = '75';
    };
    return {x: x,
            y: y}
}
function pixel_to_chess(pixel) {
    if        (pixel.x >= 0 && pixel.x < 150) {
        x = 'A';
    } else if (pixel.x >= 150 && pixel.x < 300) {
        x = 'B';
    } else if (pixel.x >= 300 && pixel.x < 450) {
        x = 'C';
    } else {
        x = 'D';
    };

    if        (pixel.y >= 0 && pixel.y < 150) {
        y = '5';
    } else if (pixel.y >= 150 && pixel.y < 300) {
        y = '4';
    } else if (pixel.y >= 300 && pixel.y < 450) {
        y = '3';
    } else if (pixel.y >= 450 && pixel.y < 600) {
        y = '2';
    } else {
        y = '1';
    };
    return {x: x,
            y: y}
}

function preload () {
    this.load.image('board4x5', 'static/images/board4x5.png');
    this.load.image('pane_white', 'static/images/pane_white.png');
    this.load.image('pane_black', 'static/images/pane_black.png');
    this.load.image('pointer', 'static/images/pointer.png');
}

function create () {
    this.socket = io('/chess');
    this.socket.on('set_pointers', (msg) => {
        for (let elem of msg.pointers) {
            pixels_coord = chess_to_pixel(elem)
            pointer = this.add.sprite(pixels_coord.x, pixels_coord.y, 'pointer');
            pointer.setAlpha(0.2)
            pointers.push(pointer)
        }
    });
    this.add.sprite(300, 375, 'board4x5');
    this.socket.on('set_figures', (msg) => {
        for (let elem of figures) {
            elem[0].destroy()
        }
        figures.length = 0;
        for (let elem of msg.figures) {
            pixels_coord = chess_to_pixel(elem);
            figure = this.add.sprite(pixels_coord.x, pixels_coord.y, elem.name);
            figure.setInteractive();
            if ( msg.active_team == team && elem.team == team ){
                this.input.setDraggable(figure);
            }
            figures.push([figure, elem]);
        }
        text = 'Turn ' + msg.active_team
        $('#player_to_move').empty().append(text)
    });

    this.socket.on('set_team', (msg) => {
        team = msg.team
        text = 'You are playing by ' + team
        $('#player_team').empty().append(text)
    })

    this.input.on('dragstart', function (pointer, gameObject) {
        gameObject.x = pointer.x;
        gameObject.y = pointer.y;
        chess_coord = pixel_to_chess(gameObject);
        drag_start.x = chess_coord.x;
        drag_start.y = chess_coord.y;
        this.scene.socket.emit('get_pointers', chess_coord);
        gameObject.setTint(0xcccccc);
    });
    this.input.on('drag', function (pointer, gameObject, dragX, dragY) {
        gameObject.x = pointer.x;
        gameObject.y = pointer.y;
    });
    this.input.on('dragend', function (pointer, gameObject) {
        for (let elem of pointers) {
            elem.destroy()
        }
        pointers.length = 0
        chess_coord = pixel_to_chess(gameObject)
        this.scene.socket.emit('move_to', {x_from: drag_start.x,
                                           y_from: drag_start.y,
                                           x_to: chess_coord.x,
                                           y_to: chess_coord.y})
        gameObject.clearTint();
    });
}

function update () {
}