CREATE TABLE IF NOT EXISTS openstack_audit.audit_blazar_computehosts (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    id VARCHAR(36),
    hypervisor_hostname VARCHAR(255),
    vcpus INT(11),
    memory_mb INT(11),
    local_gb INT(11),
    status VARCHAR(13),
    reservable TINYINT(1),
    disabled TINYINT(1),
    created_at DATETIME NULL,
    deleted_at DATETIME NULL,
    audit_event_type ENUM('INSERT', 'UPDATE', 'DELETE'),
    audit_changed_by VARCHAR(255),
    audit_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_id_changed_at (id, audit_changed_at)
)
-- ---
GRANT INSERT ON openstack_audit.audit_blazar_computehosts TO 'blazar'@'%'
-- ---
FLUSH PRIVILEGES
-- ---
CREATE OR REPLACE TRIGGER blazar.trg_computehosts_audit_ins
AFTER INSERT ON blazar.computehosts FOR EACH ROW
BEGIN
    INSERT INTO openstack_audit.audit_blazar_computehosts (
        id, hypervisor_hostname, vcpus, memory_mb, local_gb,
        status, reservable, disabled, created_at, deleted_at,
        audit_event_type, audit_changed_by
    ) VALUES (
        NEW.id, NEW.hypervisor_hostname, NEW.vcpus, NEW.memory_mb, NEW.local_gb,
        NEW.status, NEW.reservable, NEW.disabled, NEW.created_at, NEW.deleted_at,
        'INSERT', USER()
    );
END
-- ---
CREATE OR REPLACE TRIGGER blazar.trg_computehosts_audit_upd
AFTER UPDATE ON blazar.computehosts FOR EACH ROW
BEGIN
    IF NOT (OLD.status <=> NEW.status)
    OR NOT (OLD.reservable <=> NEW.reservable)
    OR NOT (OLD.disabled <=> NEW.disabled) THEN
        INSERT INTO openstack_audit.audit_blazar_computehosts (
            id, hypervisor_hostname, vcpus, memory_mb, local_gb,
            status, reservable, disabled, created_at, deleted_at,
            audit_event_type, audit_changed_by
        ) VALUES (
            NEW.id, NEW.hypervisor_hostname, NEW.vcpus, NEW.memory_mb, NEW.local_gb,
            NEW.status, NEW.reservable, NEW.disabled, NEW.created_at, NEW.deleted_at,
            'UPDATE', USER()
        );
    END IF;
END
-- ---
CREATE OR REPLACE TRIGGER blazar.trg_computehosts_audit_del
AFTER DELETE ON blazar.computehosts FOR EACH ROW
BEGIN
    INSERT INTO openstack_audit.audit_blazar_computehosts (
        id, hypervisor_hostname, vcpus, memory_mb, local_gb,
        status, reservable, disabled, created_at, deleted_at,
        audit_event_type, audit_changed_by
    ) VALUES (
        OLD.id, OLD.hypervisor_hostname, OLD.vcpus, OLD.memory_mb, OLD.local_gb,
        OLD.status, OLD.reservable, OLD.disabled, OLD.created_at, OLD.deleted_at,
        'DELETE', USER()
    );
END
