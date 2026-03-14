package com.medicalai.corebackend.exception;

public class NotFoundByIdException extends NotFoundException {
    public NotFoundByIdException(String id, String methodName) {
        super("ID ile aranan hasta bulunamadı: " + id + " Method: " + methodName);
    }
    public NotFoundByIdException(Integer id, String methodName) {
        super("ID ile aranan hasta bulunamadı: " + id + " Method: " + methodName);
    }
}
