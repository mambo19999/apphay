#pragma once
#include <algorithm>
#include <map>
#include <mutex>
#include <string>

namespace SuperBotBrain {
struct State { long long cycle=0; std::map<std::string,int> target; std::map<std::string,int> reserved; };
inline State state[10];
inline std::mutex mutex;
inline int Group(long long cycle){ return cycle<=0 ? 1 : int(((cycle-1)%3)+1); }
inline bool Active(long long cycle,int group){ return Group(cycle)==group; }
inline void Reset(int id){ std::lock_guard<std::mutex> l(mutex); state[id]=State{}; }
inline void BeginCycle(int id){ std::lock_guard<std::mutex> l(mutex); ++state[id].cycle; state[id].target.clear(); state[id].reserved.clear(); }
inline long long Cycle(int id){ std::lock_guard<std::mutex> l(mutex); return state[id].cycle; }
inline int CurrentGroup(int id){ return Group(Cycle(id)); }
inline void Need(int id,const std::string& item,int quantity){ if(quantity<=0)return; std::lock_guard<std::mutex> l(mutex); state[id].target[item]+=quantity; }
inline int NeedFor(int id,const std::string& item){ std::lock_guard<std::mutex> l(mutex); auto it=state[id].target.find(item); return it==state[id].target.end()?0:it->second; }
}

// INTEGRAZIONE DEL MAIN LOOP:
// 1. includere questo file una sola volta.
// 2. NON chiamare piu' CheckAndMakeTownVisitors().
// 3. NON chiamare RunSalesCycle(), ne' nei cicli normali ne' nei percorsi emergency.
// 4. NON usare enableRandomSaleCycle per avviare vendite.
// 5. A inizio ciclo chiamare SuperBotBrain::BeginCycle(instanceId).
// 6. Usare SuperBotBrain::CurrentGroup(instanceId) per autorizzare un solo gruppo.
// 7. Lasciare FindImage() invariata.
