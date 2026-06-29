<?php

declare(strict_types=1);

final class LeadStore
{
    private PDO $db;

    public function __construct(private string $storagePath)
    {
        $dir = dirname($storagePath);
        if (! is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        $this->db = new PDO('sqlite:' . $storagePath);
        $this->db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $this->migrate();
    }

    private function migrate(): void
    {
        $this->db->exec(<<<'SQL'
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                business_name TEXT NOT NULL,
                location TEXT NOT NULL,
                industry TEXT NOT NULL,
                contact_method TEXT,
                contact_time TEXT,
                message TEXT,
                source TEXT DEFAULT 'founding-landing',
                created_at TEXT NOT NULL
            )
        SQL);

        $columns = $this->db->query('PRAGMA table_info(leads)')->fetchAll(PDO::FETCH_ASSOC);
        $existing = array_column($columns, 'name');
        foreach ([
            'email' => 'TEXT',
            'contact_method' => 'TEXT',
            'contact_time' => 'TEXT',
        ] as $column => $type) {
            if (! in_array($column, $existing, true)) {
                $this->db->exec("ALTER TABLE leads ADD COLUMN {$column} {$type}");
            }
        }
    }

    public function save(array $data): int
    {
        $stmt = $this->db->prepare(<<<'SQL'
            INSERT INTO leads (name, phone, email, business_name, location, industry, contact_method, contact_time, message, source, created_at)
            VALUES (:name, :phone, :email, :business_name, :location, :industry, :contact_method, :contact_time, :message, :source, :created_at)
        SQL);

        $stmt->execute([
            ':name' => $data['name'],
            ':phone' => $data['phone'],
            ':email' => $data['email'] ?? '',
            ':business_name' => $data['business_name'],
            ':location' => $data['location'],
            ':industry' => $data['industry'],
            ':contact_method' => $data['contact_method'] ?? '',
            ':contact_time' => $data['contact_time'] ?? '',
            ':message' => $data['message'] ?? '',
            ':source' => $data['source'] ?? 'founding-landing',
            ':created_at' => gmdate('c'),
        ]);

        return (int) $this->db->lastInsertId();
    }
}
