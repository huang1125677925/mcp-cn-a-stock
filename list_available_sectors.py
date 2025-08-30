#!/usr/bin/env python3
"""
列出所有可用的板块名称
"""

from qtf_mcp.symbols import get_available_sectors

def main():
    sectors = get_available_sectors()
    
    print("所有可用板块名称:")
    print("=" * 50)
    
    # 按字母排序
    sectors.sort()
    
    # 过滤和分组
    ai_related = []
    new_energy = []
    medicine = []
    semiconductor = []
    others = []
    
    for sector in sectors:
        sector_lower = sector.lower()
        if "人工智能" in sector or "ai" in sector_lower or "智能" in sector_lower:
            ai_related.append(sector)
        elif "新能源" in sector or "光伏" in sector_lower or "电池" in sector_lower:
            new_energy.append(sector)
        elif "医药" in sector_lower or "医疗" in sector_lower or "生物" in sector_lower:
            medicine.append(sector)
        elif "半导体" in sector_lower or "芯片" in sector_lower or "集成电路" in sector_lower:
            semiconductor.append(sector)
        else:
            others.append(sector)
    
    print("人工智能相关板块:")
    for s in ai_related[:10]:
        print(f"  - {s}")
    
    print("\n新能源相关板块:")
    for s in new_energy[:10]:
        print(f"  - {s}")
    
    print("\n医药相关板块:")
    for s in medicine[:10]:
        print(f"  - {s}")
    
    print("\n半导体相关板块:")
    for s in semiconductor[:10]:
        print(f"  - {s}")
    
    print(f"\n其他板块: {len(others)}个")
    for s in others[:20]:
        print(f"  - {s}")

if __name__ == "__main__":
    main()