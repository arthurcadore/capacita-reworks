#!/bin/bash
## Script para realizar para desabilitar serviços de rede padrão para liberar o acesso a recursos de rede (portas UDP) para os containers Docker:

read -p "Escolha se deseja inicializar (true) ou desativar (false) o appliance ZTP: " opcao

if [[ "$opcao" == "true" ]]; then
    echo "Realizando o build do appliance ZTP..."
    docker compose build
    echo "Desabilitando o DHCP nativo..."
    sudo systemctl stop systemd-networkd.socket
    sudo systemctl stop systemd-networkd
    echo "Verificando status dos serviços:"
    sudo systemctl status systemd-networkd.socket
    sudo systemctl status systemd-networkd
    echo "verificando status das portas:"
    sudo ss -lnu
    sleep 10
    echo "Iniciando o appliance ZTP..."
    docker compose up &
elif [[ "$opcao" == "false" ]]; then
    echo "Deligando o appliance ZTP..."
    docker compose down

    echo "Habilitando o DHCP nativo..."
    sudo systemctl start systemd-networkd.socket
    sudo systemctl start systemd-networkd

    echo "Verificando status dos serviços:"
    sudo systemctl status systemd-networkd.socket
    sudo systemctl status systemd-networkd
    sudo netplan apply
    sudo ss -lnu
else
    echo "Opção inválida. Use 'true' para habilitar ou 'false' para desabilitar o appliance ZTP."
fi
