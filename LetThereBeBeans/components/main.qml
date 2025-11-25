import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 600
    height: 350
    title: "Hyperspectral"
    
    Row {
        anchors.fill: parent
        spacing: 0
        
        Loader {
            width: 200
            height: 350
            source: "XWingController.qml"
        }
        
        Column {
            width: 400
            height: 350
            spacing: 0
            
            Loader {
                width: 400
                height: 300
                source: "CornerstoneController.qml"
            }
            
            Loader {
                width: 400
                height: 50
                source: "FileSaveSelector.qml"
            }
        }
    }
}