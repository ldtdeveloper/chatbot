import { toast } from "sonner";

export const showSuccess =(message) =>
    toast.success(message,{duration:2000})

export const showError = (message) =>
    toast.error(message,{duration: 2000})