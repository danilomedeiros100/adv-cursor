"use client";

import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { X, Check, Search } from "lucide-react";

interface Option {
  id: string;
  label: string;
  sublabel?: string;
  description?: string;
}

interface SearchableSelectProps {
  placeholder: string;
  searchFunction: (term: string) => Promise<Option[]>;
  onSelect: (option: Option) => void;
  selectedOptions?: Option[];
  multiple?: boolean;
  required?: boolean;
  label: string;
  disabled?: boolean;
}

export function SearchableSelect({
  placeholder,
  searchFunction,
  onSelect,
  selectedOptions = [],
  multiple = false,
  required = false,
  label,
  disabled = false
}: SearchableSelectProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [options, setOptions] = useState<Option[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const searchOptions = async (term: string) => {
    if (!term || term.length < 2) {
      setOptions([]);
      return;
    }

    try {
      setLoading(true);
      const results = await searchFunction(term);
      // Garantir que results seja sempre um array
      if (Array.isArray(results)) {
        setOptions(results);
      } else {
        console.warn("Resultado da busca não é um array:", results);
        setOptions([]);
      }
    } catch (error) {
      console.error("Erro na busca:", error);
      setOptions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (option: Option) => {
    if (!multiple) {
      setSearchTerm(option.label);
      setIsOpen(false);
    } else {
      setSearchTerm("");
    }
    onSelect(option);
    setOptions([]);
  };

  const isSelected = (option: Option) => {
    return selectedOptions.some(selected => selected.id === option.id);
  };

  // Fechar dropdown ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      
      <div className="relative" ref={dropdownRef}>
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            ref={inputRef}
            placeholder={placeholder}
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              searchOptions(e.target.value);
              setIsOpen(true);
            }}
            onFocus={() => {
              if (searchTerm.length >= 2) {
                setIsOpen(true);
              }
            }}
            className="pl-10"
            disabled={disabled}
          />
        </div>

        {/* Dropdown de resultados */}
        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
            {loading && (
              <div className="px-4 py-2 text-sm text-gray-500">
                Buscando...
              </div>
            )}
            
            {!loading && options.length === 0 && searchTerm.length >= 2 && (
              <div className="px-4 py-2 text-sm text-gray-500">
                Nenhum resultado encontrado
              </div>
            )}
            
            {!loading && options.map((option) => (
              <div
                key={option.id}
                className={`px-4 py-2 hover:bg-gray-100 cursor-pointer border-b last:border-b-0 ${
                  isSelected(option) ? 'bg-blue-50' : ''
                }`}
                onClick={() => handleSelect(option)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="font-medium">{option.label}</div>
                    {option.sublabel && (
                      <div className="text-sm text-gray-600">{option.sublabel}</div>
                    )}
                    {option.description && (
                      <div className="text-xs text-gray-500">{option.description}</div>
                    )}
                  </div>
                  {isSelected(option) && (
                    <Check className="w-4 h-4 text-blue-600" />
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Itens selecionados (para seleção múltipla) */}
      {multiple && selectedOptions.length > 0 && (
        <div className="space-y-1">
          {selectedOptions.map((option) => (
            <div 
              key={option.id} 
              className="flex items-center justify-between p-2 bg-blue-50 border border-blue-200 rounded-md"
            >
              <div>
                <span className="text-sm font-medium text-blue-800">{option.label}</span>
                {option.sublabel && (
                  <span className="ml-2 text-xs text-blue-600">{option.sublabel}</span>
                )}
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => onSelect(option)} // Remover da seleção
                className="h-6 w-6 p-0 text-blue-600 hover:text-blue-800"
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Item selecionado (para seleção única) */}
      {!multiple && selectedOptions.length > 0 && (
        <div className="p-2 bg-green-50 border border-green-200 rounded-md">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium text-green-800">
                {selectedOptions[0].label}
              </span>
              {selectedOptions[0].sublabel && (
                <span className="ml-2 text-xs text-green-600">
                  {selectedOptions[0].sublabel}
                </span>
              )}
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => onSelect(selectedOptions[0])} // Remover seleção
              className="h-6 w-6 p-0 text-green-600 hover:text-green-800"
            >
              <X className="w-3 h-3" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
