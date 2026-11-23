export type PlatformLegendMode = 'eightbitdo' | 'nintendo' | 'xbox' | 'playstation';

export type ChassisFinish = 'sky_blue' | 'obsidian' | 'galaxy' | 'arctic' | 'cyberpunk';

export type HardwareTarget = 'pico2w' | 'picow';

export interface ChassisFinishMeta {
  id: ChassisFinish;
  name: string;
  description: string;
  shellColor: number;
  gripColor: number;
  metalColor: number;
  accentColor: number;
  emissiveColor: number;
  metalness: number;
  roughness: number;
}

export const CHASSIS_FINISHES: Record<ChassisFinish, ChassisFinishMeta> = {
  sky_blue: {
    id: 'sky_blue',
    name: '8BitDo Sky Blue',
    description: 'Authentic 8BitDo Ultimate 2C pastel Sky Blue with Cloud White base and Periwinkle controls',
    shellColor: 0xc7daf6,
    gripColor: 0xf8fafc,
    metalColor: 0x9cb8ed,
    accentColor: 0x38bdf8,
    emissiveColor: 0x22d3ee,
    metalness: 0.10,
    roughness: 0.35,
  },
  obsidian: {
    id: 'obsidian',
    name: 'Obsidian Stealth',
    description: 'Matte midnight black with brushed gunmetal titanium',
    shellColor: 0x111726,
    gripColor: 0x090d16,
    metalColor: 0x94a3b8,
    accentColor: 0x38bdf8,
    emissiveColor: 0x38bdf8,
    metalness: 0.15,
    roughness: 0.4,
  },
  galaxy: {
    id: 'galaxy',
    name: 'Cosmic Nebula',
    description: 'Deep iridescent cosmic violet',
    shellColor: 0x1f143d,
    gripColor: 0x0d071a,
    metalColor: 0xc084fc,
    accentColor: 0xa855f7,
    emissiveColor: 0xc084fc,
    metalness: 0.25,
    roughness: 0.35,
  },
  arctic: {
    id: 'arctic',
    name: 'Ceramic Arctic',
    description: 'Clean frosted ceramic white with mirror chrome hardware',
    shellColor: 0xf1f5f9,
    gripColor: 0xe2e8f0,
    metalColor: 0xd4d4d8,
    accentColor: 0x0ea5e9,
    emissiveColor: 0x38bdf8,
    metalness: 0.08,
    roughness: 0.3,
  },
  cyberpunk: {
    id: 'cyberpunk',
    name: 'Cyberpunk Neon',
    description: 'Tactical matte charcoal with neon amber & cyan accents',
    shellColor: 0x18181b,
    gripColor: 0x09090b,
    metalColor: 0x71717a,
    accentColor: 0xf59e0b,
    emissiveColor: 0x10b981,
    metalness: 0.2,
    roughness: 0.45,
  },
};

export interface PlatformMeta {
  id: PlatformLegendMode;
  name: string;
  brand: string;
  connectionType: string;
  supportedHardware: HardwareTarget[];
  primaryAccent: string;
}

export const PLATFORM_METAS: Record<PlatformLegendMode, PlatformMeta> = {
  eightbitdo: {
    id: 'eightbitdo',
    name: '8BitDo Ultimate 2C (BAYX + L4/R4)',
    brand: '8BitDo',
    connectionType: 'Bluetooth Classic & BLE',
    supportedHardware: ['pico2w', 'picow'],
    primaryAccent: '#38bdf8',
  },
  nintendo: {
    id: 'nintendo',
    name: 'Nintendo Switch (BAYX)',
    brand: 'Nintendo',
    connectionType: 'Bluetooth Classic BR/EDR',
    supportedHardware: ['pico2w', 'picow'],
    primaryAccent: '#f43f5e',
  },
  xbox: {
    id: 'xbox',
    name: 'Xbox Wireless (ABXY)',
    brand: 'Microsoft Xbox',
    connectionType: 'BLE 5.0 & Bluetooth Classic',
    supportedHardware: ['pico2w', 'picow'],
    primaryAccent: '#4ade80',
  },
  playstation: {
    id: 'playstation',
    name: 'PlayStation (DualSense / DualShock)',
    brand: 'Sony PlayStation',
    connectionType: 'Bluetooth Classic BR/EDR',
    supportedHardware: ['pico2w', 'picow'],
    primaryAccent: '#38bdf8',
  },
};

export interface DiscoveredBluetoothDevice {
  mac: string;
  name: string;
  type: PlatformLegendMode | 'generic';
  rssi: number;
  paired: boolean;
  autoConnect?: boolean;
  saved?: boolean;
}
