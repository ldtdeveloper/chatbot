import Toastify from "toastify-js";
import "toastify-js/src/toastify.css";

export const showSuccess =(message) =>
    Toastify({
        text: message,
        duration: 2000,
        gravity: "top",
        position: "center",
        backgroundColor: "#16a34a",
        style: {
            borderRadius: "10px",
            width: "350px",       // set your desired width
            textAlign: "left"   // optional, centers the text
        }
    }).showToast();

export const showError = (message) =>
    Toastify({
        text: message,
        duration: 2000,
        gravity: "top",
        position: "center",
        backgroundColor: "#dc2626",
        style: {
            borderRadius: "10px",
            width: "350px",       // set your desired width
            textAlign: "left"   // optional, centers the text
        }
    }).showToast();